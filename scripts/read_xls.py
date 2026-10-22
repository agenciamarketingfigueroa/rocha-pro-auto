"""Small, dependency-free reader for the BIFF8 workbook supplied with this project.

It deliberately reads cell values only; formulas are never evaluated. It is not a
general XLS implementation; the importer validates its required columns.
"""

from __future__ import annotations

import struct
from pathlib import Path


def u16(data, at=0):
    return struct.unpack_from("<H", data, at)[0]


def u32(data, at=0):
    return struct.unpack_from("<I", data, at)[0]


def records(data, start=0):
    at = start
    while at + 4 <= len(data):
        kind, size = struct.unpack_from("<HH", data, at)
        at += 4
        if at + size > len(data):
            raise ValueError("Truncated BIFF record")
        yield kind, data[at : at + size], at - 4
        at += size


def workbook_stream(path: Path):
    raw = path.read_bytes()
    if raw[:8] != bytes.fromhex("D0CF11E0A1B11AE1"):
        raise ValueError("Not an OLE2 XLS file")
    sector_size = 1 << u16(raw, 30)
    mini_size = 1 << u16(raw, 32)
    if sector_size not in (512, 4096) or mini_size != 64:
        raise ValueError("Unsupported OLE2 sector size")
    def sector(sid):
        at = (sid + 1) * sector_size
        return raw[at : at + sector_size]
    fat_sids = [u32(raw, 76 + 4 * i) for i in range(109)]
    fat_sids = [sid for sid in fat_sids if sid < 0xFFFFFFFA]
    difat = u32(raw, 68)
    while difat < 0xFFFFFFFA:
        block = sector(difat)
        fat_sids += [u32(block, 4 * i) for i in range(sector_size // 4 - 1) if u32(block, 4 * i) < 0xFFFFFFFA]
        difat = u32(block, sector_size - 4)
    fat = [u32(sector(sid), i) for sid in fat_sids for i in range(0, sector_size, 4)]
    def chain(sid, table, read_sector):
        seen = set()
        chunks = []
        while sid < 0xFFFFFFFA:
            if sid in seen or sid >= len(table):
                raise ValueError("Invalid OLE2 chain")
            seen.add(sid)
            chunks.append(read_sector(sid))
            sid = table[sid]
        return b"".join(chunks)
    directory = chain(u32(raw, 48), fat, sector)
    entries = []
    for at in range(0, len(directory), 128):
        d = directory[at : at + 128]
        if len(d) < 128 or not d[66]:
            continue
        name = d[: u16(d, 64) - 2].decode("utf-16le", "replace")
        entries.append((name, d[66], u32(d, 116), struct.unpack_from("<Q", d, 120)[0]))
    root = next(e for e in entries if e[1] == 5)
    book = next(e for e in entries if e[0] in ("Workbook", "Book"))
    if book[3] >= u32(raw, 56):
        return chain(book[2], fat, sector)[: book[3]]
    mini_fat = chain(u32(raw, 60), fat, sector)
    mini_table = [u32(mini_fat, i) for i in range(0, len(mini_fat), 4)]
    mini_stream = chain(root[2], fat, sector)
    return chain(book[2], mini_table, lambda sid: mini_stream[sid * mini_size : (sid + 1) * mini_size])[: book[3]]


def shared_strings(parts):
    """Decode BIFF8 SST, including continuation boundaries in character data."""
    payloads = [memoryview(part) for part in parts]
    part_no, pos = 0, 0
    def take(n):
        nonlocal part_no, pos
        out = bytearray()
        while n:
            if part_no >= len(payloads):
                raise ValueError("Truncated SST")
            available = len(payloads[part_no]) - pos
            if not available:
                part_no += 1
                pos = 0
                continue
            count = min(n, available)
            out.extend(payloads[part_no][pos : pos + count])
            pos += count
            n -= count
        return bytes(out)
    take(4)  # total occurrences
    count = u32(take(4))
    strings = []
    for _ in range(count):
        length = u16(take(2))
        flags = take(1)[0]
        rich_count = u16(take(2)) if flags & 8 else 0
        ext_size = u32(take(4)) if flags & 4 else 0
        wide = bool(flags & 1)
        chars = []
        remaining = length
        while remaining:
            if pos == len(payloads[part_no]):
                part_no += 1
                pos = 0
                wide = bool(take(1)[0] & 1)
            available = (len(payloads[part_no]) - pos) // (2 if wide else 1)
            n = min(remaining, available)
            if not n:
                raise ValueError("Broken SST character boundary")
            chars.append(take(n * (2 if wide else 1)).decode("utf-16le" if wide else "cp1252", "replace"))
            remaining -= n
        if rich_count:
            take(rich_count * 4)
        if ext_size:
            take(ext_size)
        strings.append("".join(chars))
    return strings


def load_xls(path: Path):
    data = workbook_stream(path)
    globals_records = list(records(data))
    sheets = []
    sst_parts = []
    in_sst = False
    for kind, value, _ in globals_records:
        if kind == 0x0085:
            size = value[6]
            wide = value[7] & 1
            name = value[8 : 8 + size * (2 if wide else 1)].decode("utf-16le" if wide else "latin1")
            sheets.append((name, u32(value)))
        if kind == 0x00FC:
            sst_parts.append(value)
            in_sst = True
        elif kind == 0x003C and in_sst:
            sst_parts.append(value)
        else:
            in_sst = False
    strings = shared_strings(sst_parts) if sst_parts else []
    result = {}
    for name, offset in sheets:
        cells = {}
        for kind, value, _ in records(data, offset):
            if kind == 0x000A:
                break
            if kind == 0x00FD:  # LABELSST
                row, col = struct.unpack_from("<HH", value)
                cells[(row, col)] = strings[u32(value, 6)]
            elif kind == 0x0204:  # LABEL
                row, col = struct.unpack_from("<HH", value)
                cells[(row, col)] = value[8 : 8 + u16(value, 6)].decode("cp1252", "replace")
            elif kind == 0x0203:  # NUMBER
                row, col = struct.unpack_from("<HH", value)
                number = struct.unpack_from("<d", value, 6)[0]
                cells[(row, col)] = str(int(number)) if number.is_integer() else str(number)
            elif kind == 0x027E:  # RK
                row, col = struct.unpack_from("<HH", value)
                cells[(row, col)] = decode_rk(value[6:10])
            elif kind == 0x00BD:  # MULRK
                row, first = struct.unpack_from("<HH", value)
                last = u16(value, len(value) - 2)
                for col in range(first, last + 1):
                    cells[(row, col)] = decode_rk(value[6 + 6 * (col - first) : 10 + 6 * (col - first)])
        rows = []
        if cells:
            for row in range(max(r for r, _ in cells) + 1):
                rows.append([cells.get((row, col), "") for col in range(max(c for r, c in cells if r == row) + 1)] if any(r == row for r, _ in cells) else [])
        result[name] = rows
    return result


def decode_rk(value):
    raw = u32(value)
    if raw & 2:
        number = struct.unpack("<i", value)[0] >> 2
    else:
        number = struct.unpack("<d", b"\0\0\0\0" + struct.pack("<I", raw & ~3))[0]
    if raw & 1:
        number /= 100
    return str(int(number)) if float(number).is_integer() else str(number)


if __name__ == "__main__":
    import json
    import sys
    result = load_xls(Path(sys.argv[1]))
    print(json.dumps({name: {"rows": len(rows), "preview": rows[:8]} for name, rows in result.items()}, ensure_ascii=False, indent=2))
