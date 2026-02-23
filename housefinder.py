
# Housing Finder Web App for renting houses

import os
from flask import Flask, render_template_string, request, redirect, url_for
from werkzeug.utils import secure_filename
import threading
import webbrowser


# Flask setup

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


# Sample Data

houses = [
    {"id": 1, "title": "2 Bedroom Apartments yes this is the change just for practice", "location": "Kampala, Uganda", "price": "$250/month", "price_value": 250, "description": "Spacious apartment with balcony.", "images": []},
    {"id": 2, "title": "Single Room", "location": "Entebbe, Uganda", "price": "$80/month", "price_value": 80, "description": "Affordable room, near the airport.", "images": []},
    {"id": 3, "title": "3 Bedroom House", "location": "Jinja, Uganda", "price": "$400/month", "price_value": 400, "description": "Family house near the Nile.", "images": []}
]


# Helper functions

def get_cities():
    return sorted(set(h["location"].split(",")[0] for h in houses))

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

PLACEHOLDER_IMAGE = "https://via.placeholder.com/400x250?text=No+Image"


# Base HTML layout

layout = """
<!DOCTYPE html>
<html>
<head>
    <title>House Finder</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #f2f6f9; }
        nav { background: #1e3d59; padding: 15px; display: flex; justify-content: center; flex-wrap: wrap; }
        nav a { color: white; margin: 5px 15px; text-decoration: none; font-weight: bold; font-size: 18px; transition: 0.3s; }
        nav a:hover { color: #ffd166; text-decoration: underline; }
        .container { max-width: 1000px; margin: 30px auto; padding: 20px; }
        h1 { color: #1e3d59; font-size: 36px; margin-bottom: 20px; text-align: center; }
        .card { background: #fff; padding: 20px; margin-bottom: 25px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); transition: transform 0.2s; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.15); }
        .title { font-size: 24px; font-weight: bold; color: #1e3d59; margin-bottom: 5px; }
        .location { color: #555; font-size: 18px; margin-bottom: 5px; }
        .price { color: #28a745; font-weight: bold; font-size: 20px; margin-bottom: 10px; }
        .description { font-size: 16px; margin-bottom: 10px; }
        form { margin-bottom: 25px; padding: 20px; background: #ffffff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        select, input[type="number"], input[type="text"], textarea, input[type="file"] { padding: 10px; margin: 8px 0; width: 100%; border-radius: 8px; border: 1px solid #ccc; font-size: 16px; }
        button { padding: 12px 25px; background: #1e3d59; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; transition: 0.3s; }
        button:hover { background: #3a5a78; }
        .filters { margin-bottom: 20px; color: #333; font-size: 18px; }
        .details { background: #fff; padding: 30px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .back-link { display: inline-block; margin-top: 20px; text-decoration: none; color: #1e3d59; font-size: 18px; transition: 0.3s; }
        .back-link:hover { color: #ffd166; }
        .gallery { display: flex; flex-wrap: wrap; gap: 15px; margin-top: 20px; }
        .gallery img { width: 100%; max-width: 300px; border-radius: 12px; cursor: pointer; transition: transform 0.3s; }
        .gallery img:hover { transform: scale(1.05); }
        #lightbox { display: none; position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.9); justify-content: center; align-items: center; z-index: 1000; flex-direction: column; text-align: center; }
        #lightbox-img { max-width: 90%; max-height: 80%; border-radius: 12px; margin-bottom: 10px; }
        .close { position: absolute; top: 20px; right: 30px; color: white; font-size: 40px; cursor: pointer; }
        .prev, .next { cursor: pointer; position: absolute; top: 50%; width: auto; padding: 16px; margin-top: -22px; color: white; font-weight: bold; font-size: 30px; user-select: none; }
        .prev { left: 20px; }
        .next { right: 20px; }
        .prev:hover, .next:hover { color: #ffd166; }
        @media (max-width: 600px) {
            .card { padding: 15px; }
            nav { flex-direction: column; }
        }
    </style>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/houses">Houses</a>
        <a href="/contact">Contact</a>
        <a href="/admin">Admin</a>
    </nav>
    <div class="container">
        {{ content|safe }}
    </div>
</body>
</html>
"""


# Home

@app.route("/")
def home():
    content = "<h1>Welcome to House Finder</h1><p>Find affordable and convenient housing in Uganda. Browse houses, apartments, and rooms in different cities.</p>"
    return render_template_string(layout, content=content)


# Houses list

@app.route("/houses")
def house_list():
    selected_city = request.args.get("city", "")
    max_price = request.args.get("max_price")
    sort_by = request.args.get("sort", "")

    filtered = houses
    if selected_city:
        filtered = [h for h in filtered if h["location"].startswith(selected_city)]
    if max_price:
        try:
            max_price_val = float(max_price)
            filtered = [h for h in filtered if h["price_value"] <= max_price_val]
        except ValueError:
            pass

    if sort_by == "low_high":
        filtered = sorted(filtered, key=lambda h: h["price_value"])
    elif sort_by == "high_low":
        filtered = sorted(filtered, key=lambda h: h["price_value"], reverse=True)

    city_options = "<option value=''>All Locations</option>"
    for city in get_cities():
        sel = "selected" if city == selected_city else ""
        city_options += f"<option value='{city}' {sel}>{city}</option>"

    sort_options = f"""
    <option value="" {"selected" if sort_by=="" else ""}>Default</option>
    <option value="low_high" {"selected" if sort_by=="low_high" else ""}>Price: Low → High</option>
    <option value="high_low" {"selected" if sort_by=="high_low" else ""}>Price: High → Low</option>
    """

    search_form = f"""
    <h1>Available Houses</h1>
    <form method="get" action="/houses">
        <select name="city">{city_options}</select>
        <input type="number" name="max_price" placeholder="Max price ($)" value="{max_price if max_price else ''}">
        <select name="sort">{sort_options}</select>
        <button type="submit">Search</button>
    </form>
    """

    applied_filters = ""
    if selected_city or max_price or sort_by:
        applied_filters = "<div class='filters'><strong>Filters:</strong> "
        if selected_city: applied_filters += f"City = {selected_city} "
        if max_price: applied_filters += f"| Max Price = ${max_price} "
        if sort_by == "low_high": applied_filters += "| Sorted by Price (Low → High)"
        elif sort_by == "high_low": applied_filters += "| Sorted by Price (High → Low)"
        applied_filters += "</div>"

    houses_html = ""
    if filtered:
        for h in filtered:
            img_url = h["images"][0] if h["images"] else PLACEHOLDER_IMAGE
            houses_html += f"""
            <div class='card'>
                <img src='{img_url}' style='width:100%;max-height:250px;border-radius:12px;margin-bottom:10px;object-fit:cover;'>
                <div class='title'>{h['title']}</div>
                <div class='location'>📍 {h['location']}</div>
                <div class='price'>💲 {h['price']}</div>
                <div class='description'>{h['description']}</div>
                <a href="/house/{h['id']}">➡ View Details</a>
            </div>
            """
    else:
        houses_html = "<p>No houses match your search.</p>"

    return render_template_string(layout, content=search_form + applied_filters + houses_html)


# House details

@app.route("/house/<int:house_id>")
def house_details(house_id):
    h = next((x for x in houses if x["id"]==house_id), None)
    if not h:
        return render_template_string(layout, content="<h1>House not found</h1>")

    imgs = h["images"] or [PLACEHOLDER_IMAGE]
    gallery_html = "<div class='gallery'>" + "".join([f"<img src='{img}' onclick='openLightbox({i})'>" for i,img in enumerate(imgs)]) + "</div>"

    gallery_html += """
    <div id="lightbox">
        <span class="close" onclick="closeLightbox()">&times;</span>
        <img id="lightbox-img" src="">
        <div id="caption"></div>
        <a class="prev" onclick="changeSlide(-1)">&#10094;</a>
        <a class="next" onclick="changeSlide(1)">&#10095;</a>
    </div>
    <script>
        let currentIndex=0; let images=""" + str(imgs) + """;
        function openLightbox(i){currentIndex=i;document.getElementById('lightbox').style.display='flex';update(); }
        function closeLightbox(){document.getElementById('lightbox').style.display='none'; }
        function changeSlide(n){currentIndex+=n;if(currentIndex<0)currentIndex=images.length-1;if(currentIndex>=images.length)currentIndex=0;update();}
        function update(){document.getElementById('lightbox-img').src=images[currentIndex];document.getElementById('caption').innerText='Image '+(currentIndex+1)+' of '+images.length;}
    </script>
    """

    content = f"""
    <div class='details'>
        <h1>{h['title']}</h1>
        <div class='location'>📍 {h['location']}</div>
        <div class='price'>💲 {h['price']}</div>
        <div class='description'>{h['description']}</div>
        {gallery_html}
        <a href='/houses' class='back-link'>⬅ Back to Houses</a>
    </div>
    """
    return render_template_string(layout, content=content)


# Contact page

@app.route("/contact")
def contact():
    content = "<h1>Contact Us</h1><p>Email: support@housefinder.com<br>Phone: +256 700 123456</p>"
    return render_template_string(layout, content=content)


# Admin page (Add houses + upload images)

@app.route("/admin", methods=["GET","POST"])
def admin():
    message=""
    if request.method=="POST":
        title = request.form.get("title")
        location = request.form.get("location")
        price = request.form.get("price")
        desc = request.form.get("description")
        imgs = request.files.getlist("images")
        if title and location and price:
            try: price_val=int(price)
            except: message="Price must be a number."
            else:
                new_id=max([h["id"] for h in houses])+1 if houses else 1
                img_paths=[]
                for img in imgs:
                    if img.filename!="":
                        fname=secure_filename(f"{new_id}_{img.filename}")
                        fpath=os.path.join(app.config["UPLOAD_FOLDER"], fname)
                        img.save(fpath)
                        img_paths.append("/"+fpath.replace("\\","/"))
                houses.append({"id":new_id,"title":title,"location":location,"price":f"${price}/month","price_value":price_val,"description":desc,"images":img_paths})
                message=f"House '{title}' added successfully!"
        else:
            message="Please fill in required fields."

    content=f"""
    <h1>Admin Panel - Add New House</h1>
    <p style='color:green'>{message}</p>
    <form method="post" enctype="multipart/form-data">
        <input type="text" name="title" placeholder="House Title" required><br><br>
        <input type="text" name="location" placeholder="Location (City, Country)" required><br><br>
        <input type="number" name="price" placeholder="Price ($/month)" required><br><br>
        <textarea name="description" placeholder="Description" rows="4"></textarea><br><br>
        <label>Upload Images (multiple allowed):</label><br>
        <input type="file" name="images" multiple><br><br>
        <button type="submit">Add House</button>
    </form>
    <br><a href='/houses' class='back-link'>⬅ Back to Houses</a>
    """
    return render_template_string(layout, content=content)

# Auto open browser

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


# Run app

if __name__=="__main__":
    threading.Timer(1.5, open_browser).start()

    app.run(debug=True, host="127.0.0.1", port=5000)
