-- this will either return "links" if the program needs to scrape the links or it will return "scrape" if it needs to scrape for groceries
--
-- If it detects that it is the top item it will return the html in the links category
-- If it knows that it is not the top item it click the "view more" button and scroll to the bottom of the page and return the html in the scrape category
function scrollDown(splash)
  splash.scroll_position = {y=3000}
  assert(splash:wait(.2))
  return string.len(splash:html())
end

function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(10))

  -- Look for the view more button and click it
  
  splash:set_viewport_full()
  --section:not(:has(h1, h2, h3, h4, h5, h6))
  --and not element:contains('href')
  viewMore = splash:select('.view-more')
  viewMoreLink = splash:select('.view-more .clickable.link')
  if viewMore and not viewMoreLink then
    local bounds = viewMore:bounds()
    assert(viewMore:mouse_click{x=bounds.width/2, y=bounds.height/2})
  end

  -- Keep scrolling down until no more elements appear (basically old_length == new_length)
  old_length = string.len(splash:html())
  new_length = old_length + 1
  while old_length ~= new_length do
    old_length = new_length
    new_length = scrollDown(splash)
  end
  return splash:html()
  --return {
  --  html = splash:html(),
  --  png  = splash:png(),
  --  har  = splash:har(),
    --old_length = old_length,
    --new_length = new_length,
  --}
end

  