for section_td  in soup.fetch('td', {'class' : 'alt1Active'}):
  for div_child in section_td.findChildren('div'):
    for a_child in div_child.findChildren('a'):
      a_child.text
