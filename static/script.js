document.addEventListener("DOMContentLoaded", function () {
  loadTasks();

  document.getElementById("task-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const taskName = document.getElementById("task-name").value;  // use consistent ID
    const duration = parseInt(document.getElementById("task-duration").value);
    const urgency = document.getElementById("task-urgency").value;
    const dueDate = document.getElementById("dueDate").value;

    scheduleAlert(taskName, dueDate);

    fetch("/add-task", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: taskName, duration, urgency, dueDate }) // backend expects "name"
    })
      .then((res) => res.json())
      .then(() => {
        this.reset();
        loadTasks();
      });
  });
});

function loadTasks() {
  fetch("/tasks")
    .then((res) => res.json())
    .then((tasks) => {
      const availableTime = parseInt(document.getElementById("available-time")?.value || 1440);
      const taskList = document.getElementById("task-suggestions");
      const completedList = document.getElementById("completed-tasks");
      taskList.innerHTML = "";
      completedList.innerHTML = "";

      const urgencyWeight = { High: 3, Medium: 2, Low: 1 };

      tasks.sort((a, b) => urgencyWeight[b.urgency] - urgencyWeight[a.urgency]);

      tasks.forEach((task) => {
        const li = document.createElement("li");
        li.innerHTML = `
          <div>
            <strong>${task.name}</strong> (${task.duration} min, ${task.urgency})<br/>
            Due: ${new Date(task.dueDate).toLocaleString()}
          </div>
        `;

        if (!task.completed && task.duration <= availableTime) {
          const actions = document.createElement("div");
          actions.className = "task-actions";

          const completeBtn = document.createElement("button");
          completeBtn.textContent = "✅";
          completeBtn.onclick = () => completeTask(task.id);

          const deleteBtn = document.createElement("button");
          deleteBtn.textContent = "🗑";
          deleteBtn.classList.add("delete");
          deleteBtn.onclick = () => deleteTask(task.id);

          actions.appendChild(completeBtn);
          actions.appendChild(deleteBtn);
          li.appendChild(actions);
          taskList.appendChild(li);
        } else if (task.completed) {
          li.innerHTML = `<div><del><strong>${task.name}</strong></del><br/><small>✅ Completed</small></div>`;
          completedList.appendChild(li);
        }
      });
    });
}

function suggestTasks() {
  loadTasks();
}

function completeTask(taskId) {
  fetch(`/complete-task/${taskId}`, {
    method: "POST"
  }).then(() => loadTasks());
}

function deleteTask(taskId) {
  fetch(`/delete-task/${taskId}`, {
    method: "DELETE"
  }).then(() => loadTasks());
}

function scheduleAlert(taskName, dueDateTime) {
  const now = new Date();
  const due = new Date(dueDateTime);

  const alertTime = new Date(due.getTime() - 5 * 60 * 1000);
  const delay = alertTime - now;

  if (delay > 0) {
    setTimeout(() => {
      alert(`⏰ Reminder: "${taskName}" is due in 5 minutes!`);
    }, delay);
  }
}

