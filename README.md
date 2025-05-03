````markdown
# 💻 CodeChat AI

CodeChat AI is an interactive, web-based coding assistant built with [Streamlit](https://streamlit.io/) and powered by Ollama's AI model `qwen2.5-coder:1.5b`. It offers a sleek UI, real-time chat features, and session-based chat storage for developers seeking smart assistance with code.

---

## 🚀 Features

- 🤖 **AI Coding Assistant** – Get real-time coding help and suggestions.
- 🧠 **Model** – Utilizes `qwen2.5-coder:1.5b` from Ollama.
- 💬 **Persistent Chat** – Stores all conversations session-wise with timestamps.
- 🧾 **User Auth System** – Secure registration and login using hashed passwords.
- 🎨 **Modern UI/UX** – Beautifully styled interface with custom CSS and responsive layout.
- 🗂 **Database** – SQLite backend with `users.db` and `messages.db` to manage users and chats.

---

## 📸 UI Preview

> ![screenshot-placeholder](https://via.placeholder.com/800x400.png?text=App+Screenshot+Here)

---

## 🔧 Setup Instructions

### 🖥️ Prerequisites

- Python 3.8+
- `streamlit`
- `ollama`
- `sqlite3`

### 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/codechat-ai.git
cd codechat-ai

# Install dependencies
pip install -r requirements.txt
````

### 🚀 Run the App

```bash
streamlit run main.py
```

---

## 🧱 Project Structure

```bash
📦 codechat-ai/
├── main.py             # Main Streamlit app
├── users.db            # User authentication data (SQLite)
├── messages.db         # Chat messages (SQLite)
├── db.json             # Additional DB config or metadata
└── README.md           # You are here!
```

---

## 🛡️ Security Notes

* Passwords are securely hashed using `bcrypt`.
* Sessions are isolated per user with timestamps and history.

---

## 🧠 Powered By

* [Streamlit](https://streamlit.io/)
* [Ollama](https://ollama.ai/)
* [SQLite](https://www.sqlite.org/index.html)
* [bcrypt](https://pypi.org/project/bcrypt/)

---

## 📄 License

This project is licensed under the MIT License. Feel free to use and modify it for personal or commercial use.

---

## 🙌 Acknowledgements

Special thanks to the open-source community and AI model developers for making this possible.

---

## 📬 Contact

For suggestions, feedback, or collaborations:

* GitHub: [@your-username](https://github.com/your-username)
* Email: [you@example.com](mailto:you@example.com)

---

```

Would you like me to generate a sample `requirements.txt` for this project as well?
```
