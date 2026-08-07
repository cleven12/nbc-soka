# About this repo

## English

### What is this?

A free tool that **collects Tanzania NBC Premier League (Ligi Kuu) football scores and tables**, saves them, and can share them through a simple web address (API).

### Who is it for?

| Person | How they can use it |
|--------|---------------------|
| **Journalist** | Get match results and league table without retyping from the website every time |
| **Fan / student** | Learn how open sports data works; follow the season |
| **Developer** | Build apps, bots, or dashboards on top of clean JSON data |
| **Newsroom / blog** | Automate “latest scores” pages once the API is live |

### What data?

- Match **results** and **fixtures**  
- **League table** (standings)  
- **Teams** (clubs)  
- Organised by **season** (including **2025/26** and **2026/27** when available)

### Where does the data come from?

From the public website of Ligi Kuu: [https://ligikuu.co.tz](https://ligikuu.co.tz).

This project is **not** the official league office. It only reads information that is already public and stores it in a reusable form.

### How often does it update?

When automation is enabled (GitHub Actions), about **every 6 hours**.  
You can also run an update manually.

### Will the 2026/2027 season be included?

**Yes.** The tool looks for new seasons automatically. When NBC 2026/27 matches and tables appear on the Ligi Kuu site, the next update should store them too.

### What do I need to “use” it?

- **If someone hosts the API for you:** only a web browser or a simple link (e.g. `/scores`, `/table`).  
- **If you run it yourself:** a computer with Python, or Docker (see README).

### In one sentence

> **We make NBC Ligi Kuu scores easy to reuse — for news, apps, and the public.**

---

## Swahili

### Hii ni nini?

Zana **bure** inayokusanya **matokeo na jedwali la Ligi Kuu ya NBC (Tanzania)**, kuyahifadhi, na kuyashiriki kupitia anwani rahisi ya mtandao (API).

### Inafaa nani?

| Mtu | Anaweza kufanya nini |
|-----|----------------------|
| **Mwandishi wa habari** | Kupata matokeo na jedwali bila kuandika tena kwa mkono kila siku |
| **Shabiki / mwanafunzi** | Kufuatilia msimu; kujifunza data ya soka |
| **Msanidi programu** | Kutengeneza app, bot, au dashibodi |
| **Chumba cha habari / blogu** | Kurahisisha kurasa za “matokeo ya hivi karibuni” |

### Data gani?

- **Matokeo** ya mechi na mechi zijazo  
- **Jedwali la ligi**  
- **Timu**  
- Kwa **msimu** (pamoja na **2025/26** na **2026/27** ikipatikana)

### Data inatoka wapi?

Kutoka tovuti ya umma ya Ligi Kuu: [https://ligikuu.co.tz](https://ligikuu.co.tz).

Mradi huu **si** ofisi rasmi ya ligi. Unasoma tu taarifa zilizo wazi kwa umma.

### Inasasishwa mara ngapi?

Takriban **kila masaa 6** ikiwa otomatiki imewashwa.  
Unaweza pia kusasisha mwenyewe.

### Je, msimu wa 2026/2027 utajumuishwa?

**Ndiyo.** Mfumo hutafuta misimu mipya kiotomatiki. Mechi za NBC 2026/27 zikionekana kwenye tovuti ya Ligi Kuu, sasisho linalofuata linapaswa kuziweka.

### Sentensi moja

> **Tunarahisisha matokeo ya NBC Ligi Kuu — kwa habari, programu, na umma.**

---

## Honest limits / Mipaka

- If the official site is down or changes, updates may fail until fixed.  
- Scores are only as good as the public source.  
- Always double-check important stories against the official site when needed.  
- Ikiwa tovuti rasmi imeshuka au imebadilika, sasisho linaweza kushindikana.  
- Kwa habari muhimu, thibitisha tena na chanzo rasmi inapohitajika.

## Contact / Mawasiliano

Use the GitHub repository issues for questions and improvements.
