function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(1.5))
  element = splash:select('[data-automation-id="NavigationBtn"]')
  local bounds = element:bounds()
  assert(element:mouse_click{x=bounds.width/2, y=bounds.height/2})
  assert(splash:wait(1.5))

  return {
    el = element.nodeName,
    html = splash:html(),
    png = splash:png(),
    --har = splash:har(),
  }
end