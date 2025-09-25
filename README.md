# Selenium-Autopay
Selenium Autopay with Stripe Checkout

This project demonstrates web automation using Selenium integrated with Stripe Checkout.
It automatically launches a Stripe Checkout page, fills in the payment details, and submits the payment flow.

🚀 Features

Flask backend to serve a simple web page with a Pay button

Stripe Checkout integration to generate a secure payment URL

Selenium automation to:

Open Stripe checkout

Auto-fill card details

Submit payment

📦 Requirements

Install dependencies:

pip install -r requirements.txt


Example requirements.txt:

flask
stripe
selenium
python-dotenv

⚙️ Setup

Clone the repository

git clone https://github.com/your-username/Selenium-Autopay.git
cd Selenium-Autopay


Create .env file with your Stripe Test API key:

STRIPE_API_KEY=sk_test_************************


Run Flask server

python stripe_checkout.py


→ Opens a local page at http://127.0.0.1:5000

Click Pay button
→ This generates a Stripe Checkout session & redirects to payment page.

Run Selenium automation

python autopay.py


→ Selenium launches the Checkout page, fills details, and submits automatically.

🛑 Notes

Do NOT hardcode API keys. Always store them in .env.

Use Stripe test mode keys only (never real keys in public repos).

.env and __pycache__/ should be listed in .gitignore.

📂 Project Structure
Selenium-Autopay/
│── stripe_checkout.py  # Handles session creation with Stripe
│── autopay.py          # Selenium automation script
│── requirements.txt
│── .env (ignored)      # contains STRIPE_API_KEY
│── templates/
│    └── index.html     # Simple webpage with Pay button

🎯 Portfolio Value

This project highlights:

Web Automation with Selenium

Payment Gateway Integration with Stripe

Environment Variables & Security practices
