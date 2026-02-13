{% extends 'mynews/base.html' %}
{% load static %}

{% block content %}
<link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">

<style>
.container-fluid { padding: 0 40px; }
body { background-color: #f4f7f6 !important; font-family: 'Poppins','Mukta',sans-serif; }

/* 12 Column Highlights Grid */
.hero-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    grid-auto-rows: 220px;
    gap: 12px;
    margin-bottom: 40px;
}
.hero-item { position: relative; overflow: hidden; background: #000; border-radius: 12px; height: 100%; }
.hero-item img { width: 100%; height: 100%; object-fit: cover; opacity: .7; transition: .5s; }
.hero-item:hover img { transform: scale(1.05); opacity: .85; }
.hero-content {
    position: absolute; bottom: 0; left: 0;
    padding: 15px;
    background: linear-gradient(to top, rgba(0,0,0,.95), transparent);
    width: 100%; color: #fff;
}
/* Pehla item bada dikhega professional look ke liye */
.hero-big { grid-column: span 2; grid-row: span 2; }

.clean-card {
    background:#fff; border-radius:12px; border:1px solid #eef0f2;
    margin-bottom:20px; overflow:hidden; height:100%;
    display:flex; flex-direction:column; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.clean-card img { width:100%; height:160px; object-fit:cover; }
.card-body-custom { padding:12px; flex-grow:1; }
.news-title {
    font-size:.95rem; font-weight:800; color:#1a1a1a;
    line-height:1.4; text-decoration:none!important;
}
.news-date { font-size: 11px; color: #6c757d; margin-top: 5px; display: block; }

.section-title {
    border-left:6px solid #d32f2f; padding:8px 15px;
    font-weight:900; margin:35px 0 20px; background:#f0f0f0;
}

@media (max-width:992px){
    .hero-grid { grid-template-columns: 1fr 1fr; grid-auto-rows: 180px; }
    .hero-big { grid-column: span 2; }
    .container-fluid { padding: 0 15px; }
}
</style>

{% if page_number == 1 %}
<div class="container-fluid mt-3">
    <h4 class="section-title">प्रमुख सुर्खियां</h4>
    <div class="hero-grid">
        {% for item in top_5_highlights %}
        <div class="hero-item {% if forloop.first %}hero-big{% endif %}">
            <a href="{% url 'news_detail' item.url_city|default:'news' item.slug %}">
                <img src="{% if item.image_url %}{{ item.image_url }}{% elif item.image %}{{ item.image.url }}{% else %}{% static 'logo.png' %}{% endif %}">
                <div class="hero-content">
                    <span class="badge bg-danger mb-1">{{ item.district }}</span>
                    {% if forloop.first %}
                        <h2 style="font-size: 1.5rem;">{{ item.title }}</h2>
                    {% else %}
                        <h6 style="font-size: 0.9rem;">{{ item.title|truncatechars:55 }}</h6>
                    {% endif %}
                    <small style="font-size: 10px; opacity: 0.8;"><i class="far fa-calendar-alt"></i> {{ item.date|date:"d M, Y" }}</small>
                </div>
            </a>
        </div>
        {% empty %}
        <p>Highlights available nahi hai.</p>
        {% endfor %}
    </div>
</div>
{% endif %}

<div class="container-fluid">
    <div class="row">
        <div class="col-lg-9">

            {% if page_number == 1 %}
            <h4 class="section-title">उत्तर प्रदेश (UP News)</h4>
            <div class="row">
                {% for item in up_news %}
                <div class="col-md-4 mb-4">
                    <div class="clean-card">
                        <a href="{% url 'news_detail' item.url_city|default:'news' item.slug %}">
                            <img src="{% if item.image_url %}{{ item.image_url }}{% elif item.image %}{{ item.image.url }}{% else %}{% static 'logo.png' %}{% endif %}">
                        </a>
                        <div class="card-body-custom">
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <span class="text-danger fw-bold" style="font-size:11px;">{{ item.district }}</span>
                                <span class="news-date" style="margin:0;">{{ item.date|date:"d M" }}</span>
                            </div>
                            <a href="{% url 'news_detail' item.url_city|default:'news' item.slug %}" class="news-title d-block">
                                {{ item.title|truncatechars:60 }}
                            </a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>

            <div class="row mt-4">
                <div class="col-md-6">
                    <h4 class="section-title">देश (National)</h4>
                    {% for item in national_news %}
                    <div class="d-flex bg-white p-2 mb-3 border rounded shadow-sm">
                        <img src="{% if item.image_url %}{{ item.image_url }}{% elif item.image %}{{ item.image.url }}{% else %}{% static 'logo.png' %}{% endif %}"
                             style="width:80px;height:60px;object-fit:cover;" class="rounded me-3">
                        <div>
                            <a href="{% url 'news_detail' item.url_city|default:'news' item.slug %}" class="news-title" style="font-size:13px;">
                                {{ item.title|truncatechars:50 }}
                            </a>
                            <span class="news-date">{{ item.date|date:"d M, Y" }}</span>
                        </div>
                    </div>
                    {% endfor %}
                </div>

                <div class="col-md-6">
                    <h4 class="section-title">दुनिया (World)</h4>
                    {% for item in world_news %}
                    <div class="d-flex bg-white p-2 mb-3 border rounded shadow-sm">
                        <img src="{% if item.image_url %}{{ item.image_url }}{% elif item.image %}{{ item.image.url }}{% else %}{% static 'logo.png' %}{% endif %}"
                             style="width:80px;height:60px;object-fit:cover;" class="rounded me-3">
                        <div>
                            <a href="{% url 'news_detail' item.url_city|default:'news' item.slug %}" class="news-title" style="font-size:13px;">
                                {{ item.title|truncatechars:50 }}
                            </a>
                            <span class="news-date">{{ item.date|date:"d M, Y" }}</span>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            <h4 class="section-title">ताज़ा खबरें</h4>
            <div class="row">
                {% for item in other_news %}
                <div class="col-md-4 mb-4">
                    <div class="clean-card">
                        <a href="{% url 'news_detail' item.url_city|default:'news' item.slug %}">
                            <img src="{% if item.image_url %}{{ item.image_url }}{% elif item.image %}{{ item.image.url }}{% else %}{% static 'logo.png' %}{% endif %}">
                        </a>
                        <div class="card-body-custom">
                            <span class="news-date mb-1">{{ item.date|date:"d M, Y" }}</span>
                            <a href="{% url 'news_detail' item.url_city|default:'news' item.slug %}" class="news-title">
                                {{ item.title|truncatechars:65 }}
                            </a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>

            <nav class="mt-4">
                <ul class="pagination justify-content-center">
                    {% if other_news.has_previous %}
                    <li class="page-item"><a class="page-link" href="?page={{ other_news.previous_page_number }}">Prev</a></li>
                    {% endif %}
                    <li class="page-item active"><span class="page-link bg-danger border-danger">{{ other_news.number }}</span></li>
                    {% if other_news.has_next %}
                    <li class="page-item"><a class="page-link" href="?page={{ other_news.next_page_number }}">Next</a></li>
                    {% endif %}
                </ul>
            </nav>
        </div>

        <div class="col-lg-3">
            <div class="sticky-top" style="top:20px;">
                {% include "mynews/sidebar.html" %}
            </div>
        </div>
    </div>
</div>

<script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
<script>AOS.init({duration:800,once:true});</script>

{% endblock %}
