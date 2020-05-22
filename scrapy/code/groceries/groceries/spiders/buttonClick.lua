function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(2.5))
  --click main button
  element = splash:select('[data-automation-id="NavigationBtn"]')
  local bounds = element:bounds()
  assert(element:mouse_click{x=bounds.width/2, y=bounds.height/2})
  assert(splash:wait(2))
  
  --click menu options
  --section_buttons = splash:select_all('[data-automation-id$="Btn"]')
  --section_buttons = splash:select_all('[data-automation-id$="Meat&SeafoodBtn"]')
  section_buttons = splash:select_all('[class^="NavigationPanel__item"] [data-automation-id$="Btn"]')

  --local section = section_buttons[1]
  labels={}
  hrefs={}
  for i, section in ipairs(section_buttons) do
    
    
    --hrefs[i] = elem.node:getAttribute("href")
    labels[i] = i --section.node:getAttribute("label")
    local section_bounds = section:bounds()
    assert(section:mouse_click{x=section_bounds.width/2, y=section_bounds.height/2})

    --links = splash:select_all('[data-automation-id$="Link"]')
    links = splash:select_all('[class^="NavigationPanel__aisleLink"]')
    hrefs[i] = {}
    for j, link in ipairs(links) do
      --scrape-links
      hrefs[i][j] = link.node:getAttribute("href")
    end
    
    assert(splash:wait(.1))
  end
 
  return {
    labels = labels,
    hrefs = hrefs,
    --el = element.nodeName,
    html = splash:html(),
    png = splash:png(),
    --har = splash:har(),
  }
end