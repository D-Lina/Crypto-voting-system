# 🚀 CryptoVote Backend (FastAPI)
 1. How to Run the Backend

  ✅ Step 1 — Install dependencies
  
      ```bash
       pip install -r requirements.txt
      ```
  
  ✅ Step 2 — Start the server
  
      ```bash
      uvicorn api:app --reload --port 8000
      ```
  
  ✅ Step 3 — Open API documentation : Open in browser:
  
     ```
     http://localhost:8000/docs
     ```

👉 This allows you to test all endpoints manually.

🌐 Base URL : All API endpoints are under: http://localhost:8000/pyapi


2. API Workflow (IMPORTANT) : The system follows this order:
1. **Setup election** (admin)
2. **Users vote**
3. **Close voting** (admin)
4. **Count votes** (admin)
5. **Get results**
---

3. Frontend Integration Guide : 
 ⚠️Frontend must replace ALL fake logic with real API calls.
 01. Add Base URL : In your JavaScript file:

```javascript
const API_BASE = "http://localhost:8000/pyapi";
```
02. Vote API : 
Endpoint:POST /vote
Example:
```javascript
async function submitVote(n1, n2, vote) {
  const response = await fetch(`${API_BASE}/vote`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      n1: n1,
      n2: n2,
      vote: vote
    })
  });

  const data = await response.json();

  if (!response.ok) {
    alert("❌ " + data.detail);
    return;
  }

  alert("✅ Vote accepted");
}
```
03. Setup Election (ADMIN)

POST /admin/setup
```javascript
async function setupElection(voters) {
  await fetch(`${API_BASE}/admin/setup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      pin: "1234",
      voters: voters,
      admin_primes: [61, 53],
      counter_primes: [59, 47]
    })
  });
}
```
 04. Close Voting

POST /admin/close
```javascript
async function closeVoting() {
  await fetch(`${API_BASE}/admin/close`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      pin: "1234"
    })
  });
}
```
05. Count Votes

POST /admin/count
```javascript
async function countVotes() {
  await fetch(`${API_BASE}/admin/count`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      pin: "1234"
    })
  });
}
```
 06. Get Results
GET /results
```javascript
async function getResults() {
  const res = await fetch(`${API_BASE}/results`);
  const data = await res.json();

  const container = document.getElementById("results");
  container.innerHTML = "";

  data.tally.forEach(item => {
    container.innerHTML += `<p>Vote ${item.vote}: ${item.count}</p>`;
  });
}
```
07. Admin PIN
Some endpoints require a PIN:
PIN = 1234
---

4. Common Errors

| Error           | Cause                       |
| --------------- | --------------------------- |
| 404 Not Found   | Missing `/pyapi` in URL     |
| Failed to fetch | Backend not running         |
| 400 Bad Request | Invalid data                |
| Vote rejected   | Invalid N1 or already voted |


5. Testing Checklist :Make sure this works:
[ ] Setup election
[ ] Submit vote
[ ] Close voting
[ ] Count votes
[ ] Display results

---
# 🎯 Summary
Frontend developers must:
* Replace UI logic with API calls
* Use `fetch()` to communicate with backend
* Handle success and error responses
* Display results correctly
