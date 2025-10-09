const API_BASE = "http://localhost:3000";  // Change if backend runs elsewhere
const STATE_COLORS = { "done": "gray", "work": "red" }

async function loadData() {
  const response = await fetch(`${API_BASE}/get_data`);
  const data = await response.json();

  const tbody = document.querySelector("#dataTable tbody");
  tbody.innerHTML = "";

  data.forEach(item => {
    const row = document.createElement('tr');
    row.innerHTML = `
                    <td>${item.type}</td>
                    <td>${item.lesson}</td>
                    <td>${new Date(item.date).toLocaleString()}</td>
                    <td>${item.state}</td>
                    <td>${item.comment}</td>
                `;
    row.style.backgroundColor = STATE_COLORS[item.state];
    tbody.appendChild(row);
  });
}

document.querySelector("#addForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    type: document.querySelector("#type").value,
    lesson: document.querySelector("#lesson").value,
    date: new Date(document.querySelector("#date").value).toISOString(),
    comment: document.querySelector("#comment").value
  };

  const response = await fetch(`${API_BASE}/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (response.ok) {
    alert("Data added successfully");
    e.target.reset();
    loadData();
  } else {
    alert("Error adding data");
  }
});

loadData();

