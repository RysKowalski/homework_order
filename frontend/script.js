async function checkLogin() {
  const response = await fetch("/valid");
  return response.ok ? await response.json() : false;
}

async function log_in() {
  if (checkLogin())
}

async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const status = document.getElementById("login-status");



  const response = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: username, password: password })
  });

  if (response.ok) {
    status.textContent = "Login successful.";
    document.getElementById("login-container").classList.add("hidden");
    document.getElementById("main").classList.remove("hidden");
    await loadData();
  } else {
    status.textContent = "Login failed.";
  }
}

async function loadData() {
  const response = await fetch("/get_data");
  if (!response.ok) {
    alert("Invalid token or unauthorized.");
    return;
  }

  const data = await response.json();
  const tbody = document.getElementById("table-body");
  tbody.innerHTML = "";

  data.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
            <td>${item.id}</td>
            <td>${item.type}</td>
            <td>${item.lesson}</td>
            <td>${new Date(item.date).toLocaleDateString()}</td>
            <td>${item.comment}</td>
            <td>${item.state}</td>
            <td><button onclick="deleteData(${item.id})">Delete</button></td>
        `;
    tbody.appendChild(tr);
  });
}

async function addData() {
  const data = {
    id: parseInt(document.getElementById("data-id").value),
    type: document.getElementById("data-type").value,
    lesson: document.getElementById("data-lesson").value,
    date: document.getElementById("data-date").value,
    comment: document.getElementById("data-comment").value,
    state: document.getElementById("data-state").value
  };

  const response = await fetch("/add_data", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  if (response.ok) {
    await loadData();
  } else {
    alert("Failed to add data.");
  }
}

async function deleteData(id) {
  const response = await fetch(`/delete_data?id=${id}`, {
    method: "DELETE"
  });
  if (response.ok) {
    await loadData();
  } else {
    alert("Failed to delete data.");
  }
}

document.getElementById("login-btn").addEventListener("click", login);
document.getElementById("add-btn").addEventListener("click", addData);
document.getElementById("refresh-btn").addEventListener("click", loadData);
document.getElementById("logout-btn").addEventListener("click", () => {
  document.cookie = "token=; Max-Age=0";
  document.getElementById("main").classList.add("hidden");
  document.getElementById("login-container").classList.remove("hidden");
});

document.addEventListener(log_in, document.onload())
