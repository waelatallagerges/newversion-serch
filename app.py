from flask import Flask, request, jsonify
from search import search
from filter import Filter
from storage import DBStorage
import html
from bs4 import BeautifulSoup

app = Flask(__name__)

styles = """
<style>
    .site {
        font-size: .8rem;
        color: green;
    }
    
    .snippet {
        font-size: .9rem;
        color: gray;
        margin-bottom: 30px;
    }
    
    .rel-button {
        cursor: pointer;
        color: blue;
    }
    
    .point {
        position: relative;
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background-color: #ccc;
        margin: 10px;
        cursor: pointer;
    }
    
    .point img {
        width: 100%;
        height: 100%;
    }
    
    .point .info {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.5);
        text-align: center;
        font-size: 1rem;
        color: white;
    }
</style>
<script>
const relevant = function(query, link){
    fetch("/relevant", {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
           "query": query,
           "link": link
          })
        });
}
</script>
"""

search_template = styles + """
     <form action="/" method="post">
      <input type="text" name="query">
      <input type="submit" value="Search">
    </form> 
    """

result_template = """
<div class="point">
    <img src="{image}" />
    <div class="info">
        <p><strong>URL:</strong> <a href="{url}" target="_blank">{url}</a></p>
        <p><strong>Info:</strong> {info}</p>
        <p><strong>Products/Services:</strong> {products}</p>
        <p><strong>Keywords:</strong> {keywords}</p>
        <p><strong>Product/Service Image:</strong> <img src="{product_image}" /></p>
        <p><strong>Rank:</strong> {rank}</p>
    </div>
</div>
"""

def get_products_and_image(row):
    soup = BeautifulSoup(row["html"])
    products = soup.find_all("div", {"class": "product"})
    if products:
        products = [p.get_text(strip=True) for p in products]
    else:
        products = []

    image = soup.find("img", {"class": "product-image"})
    if image:
        image = image["src"]
    else:
        image = ""

    return products, image


def run_search(query):
    results = search(query)
    fi = Filter(results)
    filtered = fi.filter()
    rendered = search_template
    filtered["snippet"] = filtered["snippet"].apply(lambda x: html.escape(x))
    for index, row in filtered.iterrows():
        soup = BeautifulSoup(row["html"])
        image = soup.find("img", {"src": True})
        if image:
            image = image["src"]
        else:
            image = ""

        products, product_image = get_products_and_image(row)

        # Add your logic to retrieve keywords here
        keywords = ""

        rendered += result_template.format(
            url=row["link"],
            info=row["info"],
            products=", ".join(products),
            keywords=keywords,
            product_image=product_image,
            rank=row["rank"],
            image=image
        )
    return rendered


def show_search_form():
    return search_template


@app.route("/", methods=['GET', 'POST'])
def search_form():
    if request.method == 'POST':
        query = request.form["query"]
        return run_search(query)
    else:
        return show_search_form()


@app.route("/relevant", methods=["POST"])
def mark_relevant():
    data = request.get_json()
    query = data["query"]
    link = data["link"]
    storage = DBStorage()
    storage.update_relevance(query, link, 10)
    return jsonify(success=True)
