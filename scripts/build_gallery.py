import os
import json

def build_html_gallery():
    # Update paths to work from scripts/ directory
    base_dir = os.path.join("..", "models")
    output_path = os.path.join("..", "index.html")
    
    # Setup the HTML boilerplate and CSS styling
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mesa Examples Gallery</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 40px; background-color: #f6f8fa; color: #24292e; }
            h1 { text-align: center; margin-bottom: 40px; }
            .grid { display: flex; gap: 20px; flex-wrap: wrap; justify-content: center; }
            .card { background: white; border: 1px solid #e1e4e8; border-radius: 8px; padding: 20px; width: 320px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: transform 0.2s; }
            .card:hover { transform: translateY(-5px); }
            .tag { display: inline-block; background: #0366d6; color: white; padding: 4px 10px; border-radius: 2em; font-size: 12px; margin-right: 5px; margin-bottom: 8px; font-weight: bold; }
            .author { color: #586069; font-size: 14px; margin-top: -10px; margin-bottom: 15px; }
            .domain { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #d73a49; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🏛️ Mesa Examples Community Gallery</h1>
        <div class="grid">
    """
    
    # Crawl the directory for metadata
    if os.path.exists(base_dir):
        for folder in os.listdir(base_dir):
            meta_path = os.path.join(base_dir, folder, "metadata.json")
            
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    data = json.load(f)
                
                # Create HTML tags for the features
                tags_html = "".join([f"<span class='tag'>{feature}</span>" for feature in data.get('features', [])])
                
                # Build the individual model card
                card = f"""
                <div class="card">
                    <div class="domain">{data.get('domain', 'General')}</div>
                    <h2>{data.get('name', 'Untitled Model')}</h2>
                    <p class="author">By {data.get('author', 'Unknown')}</p>
                    <p>{data.get('description', 'No description provided.')}</p>
                    <div>{tags_html}</div>
                    <p style="font-size: 12px; color: #6a737d; margin-top: 15px;">Complexity: <b>{data.get('complexity', 'Unknown')}</b></p>
                </div>
                """
                html_content += card
                
    html_content += "</div></body></html>"
    
    # Save the output to an index.html file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Static Gallery successfully generated at {output_path}")

if __name__ == "__main__":
    build_html_gallery()
