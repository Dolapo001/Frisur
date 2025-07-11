# 💈 Frisur Barbing Salon

Frisur Barbing Salon is a digital barbing salon platform that enables users to book appointments with their preferred stylists. Users receive confirmation and reminder emails with appointment details. This project streamlines salon scheduling and enhances customer experience through automation.

---

## 🚀 Features

- User registration and authentication
- Book appointments with barbers/stylists
- Email notifications for:
  - Appointment confirmation
  - Appointment reminders
- Admin dashboard to manage stylists and bookings
- Clean, responsive UI

---

## 🛠️ Tech Stack

**Backend**
- Django
- Django REST Framework

**Database**
- PostgreSQL

**Other Tools**
- Celery & Redis (background tasks)
- SMTP (email notifications)
- Docker (containerization)
- Git & GitHub (version control)

---


## 📦 Installation

### 1. Clone the Repository

```bash
git clone git@github.com:Dolapo001/Frisur.git
cd Frisur
```

### 2. Set Up Virtual Environment (Backend)

```bash
cd barbing_salon
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file inside the `backend/` folder:

```env
DEBUG=True
SECRET_KEY=your_secret_key
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
```

### 5. Apply Migrations and Start the Server

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

## 🧠 What I Learned

* Celery & Redis integration for background tasks
* Automated email reminders with Django SMTP
* Django project structuring for deployment
* Working with PostgreSQL in production environments
* Dockerizing Django applications

---

## 🤝 Contributing

Contributions are welcome!
Please fork the repository and submit a pull request.

For major changes, open an issue first to discuss what you'd like to propose.

---

## 📄 License

This project is licensed under the [[MIT License](https://github.com/Dolapo001/Frisur/blob/main/LICENSE).

---

## 📬 Contact

For inquiries or feature requests:

* GitHub Issues
* Email: [adedolapo.atiba@gmail.com](mailto:yadedolapo.atiba@gmail.com) 

---

## 🌟 Support This Project

If you found this helpful, please give the repo a ⭐ — it helps others discover it and supports my work!
