function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(2.5))
  --click main button
  element = splash:select('[data-automation-id="NavigationBtn"]')
  local bounds = element:bounds()
  assert(element:mouse_click{x=bounds.width/2, y=bounds.height/2})
  assert(splash:wait(2))
  
  --click menu options
  section_buttons = splash:select_all('[class^="NavigationPanel__item"] [data-automation-id$="Btn"]')

  hrefs={}
  for i, section in ipairs(section_buttons) do
    local section_bounds = section:bounds()
    --click each section
    assert(section:mouse_click{x=section_bounds.width/2, y=section_bounds.height/2})
    
    links = splash:select_all('[class^="NavigationPanel__aisleLink"]')
    for j, link in ipairs(links) do
      --scrape-links
      local href = link.node:getAttribute("href")
      table.insert(hrefs,href)    
    end
    assert(splash:wait(.1))
  end
 
  return {
    --labels = labels,
    hrefs = hrefs,
    --el = element.nodeName,
    --html = splash:html(),
    --png = splash:png(),
    --har = splash:har(),
  }
end