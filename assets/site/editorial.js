(() => {
  const buttons = Array.from(document.querySelectorAll('[data-topic]'));
  const posts = Array.from(document.querySelectorAll('[data-post-topics]'));
  buttons.forEach(button => button.addEventListener('click', () => {
    const topic = button.dataset.topic;
    buttons.forEach(b => { b.classList.toggle('active', b === button); b.setAttribute('aria-pressed', String(b === button)); });
    let count = 0;
    posts.forEach(post => { post.hidden = topic !== 'all' && !post.dataset.postTopics.split(' ').includes(topic); if (!post.hidden) count++; });
    document.querySelector('#post-count').textContent = `${count} ${count === 1 ? 'artigo' : 'artigos'}`;
  }));
})();
