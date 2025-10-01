const form = document.querySelector('#note-form');
const notesList = document.querySelector('#notes-list');
const feedback = document.querySelector('.form-feedback');
const totalNotes = document.querySelector('#total-notes');
const weeklyNotes = document.querySelector('#weekly-notes');
const composerTime = document.querySelector('#composer-time');
let editingId = null;

function noteTemplate(note) {
  const article = document.createElement('article');
  article.className = 'note-card';
  article.dataset.id = note.id;
  article.innerHTML = `
    <header>
      <h3></h3>
      <time datetime="${note.updated_at}"></time>
    </header>
    <p class="note-body"></p>
    <footer>
      <button type="button" class="icon-button" data-action="edit">수정</button>
      <button type="button" class="icon-button" data-action="delete">삭제</button>
    </footer>
  `;
  article.querySelector('h3').textContent = note.title;
  article.querySelector('time').textContent = formatDate(note.updated_at);
  article.querySelector('.note-body').textContent = note.content;
  return article;
}

function formatDate(isoString) {
  const date = new Date(isoString);
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
}

async function fetchNotes() {
  const response = await fetch('/api/notes');
  if (!response.ok) return;
  const notes = await response.json();
  notesList.innerHTML = '';
  if (!notes.length) {
    notesList.innerHTML = '<p class="empty-state">첫 노트를 작성해 나만의 타임라인을 만들어보세요.</p>';
    updateStats(notes);
    return;
  }
  notes.forEach((note) => {
    notesList.appendChild(noteTemplate(note));
  });
  updateStats(notes);
}

async function submitNote(event) {
  event.preventDefault();
  const title = form.title.value.trim();
  const content = form.content.value.trim();

  if (!title || !content) {
    feedback.textContent = '제목과 내용을 모두 입력해주세요.';
    return;
  }

  const payload = { title, content };
  const url = editingId ? `/api/notes/${editingId}` : '/api/notes';
  const method = editingId ? 'PUT' : 'POST';

  const response = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const data = response.status !== 204 ? await response.json() : null;

  if (!response.ok) {
    feedback.textContent = data?.error || '요청 처리 중 오류가 발생했습니다.';
    return;
  }

  feedback.textContent = editingId ? '노트를 업데이트했어요.' : '새로운 노트를 저장했어요!';
  form.reset();
  editingId = null;
  form.querySelector('.primary-button').textContent = '기록 저장';
  await fetchNotes();
}

async function deleteNote(id) {
  const confirmed = window.confirm('정말로 삭제하시겠어요?');
  if (!confirmed) return;
  const response = await fetch(`/api/notes/${id}`, { method: 'DELETE' });
  if (response.ok) {
    feedback.textContent = '노트를 삭제했어요.';
    await fetchNotes();
  }
}

function startEdit(noteCard) {
  const id = noteCard.dataset.id;
  const title = noteCard.querySelector('h3').textContent;
  const content = noteCard.querySelector('.note-body').textContent;
  form.title.value = title;
  form.content.value = content;
  editingId = id;
  form.querySelector('.primary-button').textContent = '기록 수정';
  feedback.textContent = '노트 수정 중입니다.';
  form.title.focus();
}

function updateStats(notes) {
  if (!totalNotes || !weeklyNotes) return;
  totalNotes.textContent = notes.length;
  const now = new Date();
  const weekAgo = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 6);
  const weeklyCount = notes.filter((note) => {
    const updated = new Date(note.updated_at);
    return updated >= weekAgo;
  }).length;
  weeklyNotes.textContent = weeklyCount;
}

function refreshComposerTime() {
  if (!composerTime) return;
  const now = new Date();
  composerTime.textContent = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')} · ${
    now.getFullYear()
  }.${String(now.getMonth() + 1).padStart(2, '0')}.${String(now.getDate()).padStart(2, '0')}`;
}

notesList?.addEventListener('click', (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;
  const action = target.dataset.action;
  const noteCard = target.closest('.note-card');
  if (!noteCard || !action) return;

  if (action === 'delete') {
    deleteNote(noteCard.dataset.id);
  }
  if (action === 'edit') {
    startEdit(noteCard);
  }
});

form?.addEventListener('submit', submitNote);

refreshComposerTime();
setInterval(refreshComposerTime, 60 * 1000);
fetchNotes();
