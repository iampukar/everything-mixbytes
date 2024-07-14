import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

async def scroll_to_bottom(page):
    previous_height = await page.evaluate("document.body.scrollHeight")
    while True:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)  # Adjust timeout as necessary
        new_height = await page.evaluate("document.body.scrollHeight")
        if new_height == previous_height:
            break
        previous_height = new_height

async def fetch_mixbytes_posts(page):
    await page.goto("https://mixbytes.io/blog")
    await scroll_to_bottom(page)  # Scroll to the bottom to load all content

    posts = await page.evaluate('''() => {
        const containers = Array.from(document.querySelectorAll('.t-container'));
        console.log('Total t-container elements:', containers.length);
        const blogs = [];
        let totalSubDivs = 0;

        containers.forEach((container, index) => {
            const subDivs = container.querySelectorAll('.t404__col.t-col.t-col_4.t-align_left');
            totalSubDivs += subDivs.length;
            console.log(`Container ${index + 1}: sub-div elements:`, subDivs.length);

            subDivs.forEach((item, subIndex) => {
                console.log(`Processing sub-div ${subIndex + 1} in container ${index + 1}`);
                const linkElement = item.querySelector('a.t404__link');
                const categoryElement = item.querySelector('.t404__tag');
                const dateElement = item.querySelector('.t404__date');
                const titleElement = item.querySelector('.t404__title');
                const descriptionElement = item.querySelector('.t404__descr');

                if (linkElement && categoryElement && dateElement && titleElement && descriptionElement) {
                    const link = `https://mixbytes.io${linkElement.getAttribute('href')}`;
                    blogs.push({
                        title: titleElement.innerText,
                        published_date: dateElement.innerText,
                        category: categoryElement.innerText,
                        description: descriptionElement.innerText,
                        link: link
                    });
                    console.log(`Added blog: ${titleElement.innerText}`);
                } else {
                    console.log('Missing elements in sub-div', subIndex + 1);
                }
            });
        });
        console.log('Total sub-divs processed:', totalSubDivs);
        return blogs;
    }''')
    return posts

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%B %d, %Y")
    except ValueError:
        return datetime.min  # Return a minimum date if parsing fails

def sort_and_remove_duplicates(posts):
    # Sort posts by published date in descending order
    posts.sort(key=lambda x: parse_date(x['published_date']), reverse=True)
    # Remove duplicates
    unique_posts = []
    seen = set()
    for post in posts:
        identifier = (post['title'].strip().lower(), post['description'].strip().lower())
        if identifier not in seen:
            seen.add(identifier)
            unique_posts.append(post)
    return unique_posts

def check_for_duplicate_titles(posts):
    titles = set()
    unique_posts = []
    duplicates = 0
    for post in posts:
        title = post['title'].strip().lower()
        if title in titles:
            duplicates += 1
        else:
            titles.add(title)
            unique_posts.append(post)
    print(f"Removed {duplicates} duplicate posts based on titles.")
    return unique_posts

def generate_readme(posts):
    readme_content = "# Everything Mixbytes\n\n"
    readme_content += "This file includes all the references and blog posts from Mixbytes.\n\n"
    readme_content += "## Getting Started\n\n"
    readme_content += "To set up the project, run the following commands:\n\n"
    readme_content += "```bash\n"
    readme_content += "chmod +x setup.sh\n"
    readme_content += "./setup.sh\n"
    readme_content += "```\n\n"
    readme_content += "| Title | Published Date | Category | Description | Link | Read |\n"
    readme_content += "|-------|----------------|----------|-------------|------|------|\n"

    for post in posts:
        read_status = "[ ]"  # All posts are unread by default
        readme_content += f"| {post['title']} | {post['published_date']} | {post['category']} | {post['description']} | [Link]({post['link']}) | {read_status} |\n"

    with open("README.md", "w") as f:
        f.write(readme_content)
    print("README.md file created.")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        mixbytes_posts = await fetch_mixbytes_posts(page)
        
        mixbytes_posts = sort_and_remove_duplicates(mixbytes_posts)
        
        # Check for duplicate titles and remove them
        mixbytes_posts = check_for_duplicate_titles(mixbytes_posts)
        
        generate_readme(mixbytes_posts)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
