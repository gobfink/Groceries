-- this will either return "links" if the program needs to scrape the links or it will return "scrape" if it needs to scrape for groceries
--
-- If it detects that it is the top item it will return the html in the links category
-- If it knows that it is not the top item it click the "view more" button and scroll to the bottom of the page and return the html in the scrape category
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(0.5))
  
  sections=splash:select_all('[class="category-filter__link"]')
  selected_section=splash:select('[class="category-filter__link"] [aria-current="page"]')
  selected_html=selected_section.node.attributes
  elements={}
  inner_html={}
  for i,node in ipairs(sections) do
    elements[i]=node.node.attributes
    inner_html[i]=node.node.innerHTML
  end
  link_html = ""
  if elements[0] == selected_html then
    link_html = splash:html()
  end
  return {
    elements = elements,
    inner_html = inner_html,
    html = splash:html(),
    png = splash:png(),
    har = splash:har(),
    selected_html = selected_html,
    link_html = link_html,
  }
end