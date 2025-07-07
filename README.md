# RobuxKingdomDjango

This repository now contains a Django project with a `main` application. The existing HTML layout is served through Django for further development.

## Quick start

Install dependencies (Django 5.x is required) and run migrations:

```bash
pip install -r requirements.txt  # or `pip install django`
python manage.py migrate
```

Launch the development server:

```bash
python manage.py runserver
```

The home page uses the layout in `robux_head_pc/index.html` and static files are served directly from the repository.

## FreeKassa integration

A payment link is generated when the user clicks the "Оплатить" button. The project uses [FreeKassa](https://freekassa.com/) SCI.

1. Register at [FreeKassa](https://freekassa.com/auth/registration?inv=FK96&input_type=hidden) and choose "Принимать платежи на сайте".
2. Confirm the domain ownership by placing the proposed HTML, banner or DNS record (you may remove it later).
3. In the merchant panel fill in the technical settings and activate the cashbox in the "Мои кассы" section.
4. Set the notification URL to `https://<your-domain>/freekassa/notify/`.
5. Create `.env` variables for `FREEKASSA_MERCHANT_ID`, `FREEKASSA_SECRET_1` and `FREEKASSA_SECRET_2` and restart the server.

The signature for the payment form is calculated as `md5("MERCHANT_ID:AMOUNT:SECRET_1:RUB:ORDER_ID")`. The notification signature is `md5("MERCHANT_ID:AMOUNT:SECRET_2:ORDER_ID")`.

On successful payment FreeKassa sends a POST request to the notification URL and a record is created in the `Order` model storing the account, account ID, order amount, paid amount and the Robux quantity.
