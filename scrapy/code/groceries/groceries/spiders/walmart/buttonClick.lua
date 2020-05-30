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
  sections={}
  for i, section in ipairs(section_buttons) do
    local section_name = section.node:getAttribute("aria-label")
    
    local section_bounds = section:bounds()
    --click each section
    assert(section:mouse_click{x=section_bounds.width/2, y=section_bounds.height/2})
    
    links = splash:select_all('[class^="NavigationPanel__aisleLink"]')
    local section_links={}
    for j, link in ipairs(links) do
      --scrape-links
      local dataId = link.node:getAttribute("data-automation-id")
      local href = link.node:getAttribute("href")
      section_links[dataId] = href
      --table.insert(ids,id)
      table.insert(hrefs,href)    
    end
    sections[section_name]=section_links
    assert(splash:wait(.1))
  end
 
  return {
    --labels = labels,
    hrefs = hrefs,
    sections = sections,
    --el = element.nodeName,
    --html = splash:html(),
    --png = splash:png(),
    --har = splash:har(),
  }
end
