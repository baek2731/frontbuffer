---
layout: archive
title: "Tech"
permalink: /categories/tech/
author_profile: false
---

{% assign posts = site.categories.tech %}
{% for post in posts %}
  {% include archive-single.html %}
{% endfor %}
