import asyncio
from playwright.async_api import async_playwright

async def fetch_mixbytes_posts(page):
    await page.goto("https://mixbytes.io/blog")

    posts = await page.evaluate('''() => {
        const items = Array.from(document.querySelectorAll('.t-container'));
        return items.map(item => {
            const linkElement = item.querySelector('a.t404__link');
            const link = linkElement ? `https://mixbytes.io${linkElement.getAttribute('href')}` : '';
            const categoryElement = item.querySelector('.t404__tag');
            const dateElement = item.querySelector('.t404__date');
            const titleElement = item.querySelector('.t404__title');
            const descriptionElement = item.querySelector('.t404__descr');

            // Check if the essential elements are not empty
            if (titleElement && dateElement && linkElement) {
                return {
                    title: titleElement.innerText,
                    published_date: dateElement.innerText,
                    link: link,
                    category: categoryElement ? categoryElement.innerText : '',
                    description: descriptionElement ? descriptionElement.innerText : ''
                };
            } else {
                return null;  // Exclude this entry if essential elements are missing
            }
        }).filter(post => post !== null);  // Filter out null entries
    }''')
    return posts

def generate_readme(posts):
    readme_content = "# Everything Mixbytes\n\n"
    readme_content += "This README file includes all the [references and blog posts](https://mixbytes.io/blog) from Mixbytes.\n\n"
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

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        mixbytes_posts = await fetch_mixbytes_posts(page)
        
        generate_readme(mixbytes_posts)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())