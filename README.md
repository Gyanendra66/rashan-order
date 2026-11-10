# rashan-order 🛒

Claude ke liye ek skill: ghar ke rashan / zaruri saman ki list banao, aur Claude us list ko Blinkit (ya Zepto, Instamart, BigBasket) par cart me daal kar, **aapki final haan ke baad**, UPI se order kar de. Schedule bhi laga sakte ho (har Sunday, har mahine ki 1 tarikh...).

A Claude skill that keeps a household grocery list and turns it into a real order on Blinkit or a similar store, paid by UPI after your final confirmation, optionally on a schedule.

## Kaise kaam karta hai

1. **List** - bas bolo: "doodh khatam ho gaya", "5 kg atta har mahine chahiye".
2. **Order** - bolo "rashan order kar do". Claude cart banata hai aur poora bill dikhata hai (items, substitute, delivery fee, total, address).
3. **Aapki haan** - "haan" bolne ke baad hi payment shuru hota hai.
4. **UPI** - request aapke phone ke UPI app me aati hai; PIN aap khud dalte ho.
5. **Record** - order ID aur total history me save ho jata hai.

## Install

**Claude Code** - `rashan-order` folder ko apne skills folder me copy karo:

```bash
git clone https://github.com/Gyanendra66/rashan-order.git
```

```bash
cp -r rashan-order/rashan-order ~/.claude/skills/
```

**Claude app (desktop / web)** - is repo ke Releases se `rashan-order.skill` file download karo aur Claude ki Settings ke Skills section me upload karo.

Zarurat: Python 3.7+ (koi extra package nahi), aur order ke liye ek browser tool jisme aap store par logged in ho (Claude in Chrome, Claude desktop app ka browser, ya computer use). Browser tool ke bina bhi list wala hissa chalta hai.

## Use karna

| Aap bolo | Kya hoga |
|---|---|
| "doodh 2 litre list me daal do" | item add |
| "atta 5 kg har 30 din me chahiye" | recurring item |
| "list dikhao" | poori list |
| "rashan order kar do" | cart -> bill -> aapki haan -> UPI |
| "har Sunday subah 9 baje order ready rakho" | schedule |
| "pichli baar kya mangwaya tha?" | history |

Pehli baar Claude ek baar budget, address ka naam aur store puchega.

## Safety (zarur padho)

- Claude kabhi UPI PIN, OTP ya card details nahi mangta aur nahi leta. Ye sirf aapke phone par rehte hain.
- Har order se pehle poora bill dikhaya jata hai; aapki haan ke bina kuch order nahi hota - scheduled run me bhi. Schedule ka matlab hai "cart tayyar, ek haan door", "sote hue paisa kat gaya" nahi.
- List me jo nahi hai (suggested items, tip, donation, membership) wo cart me nahi jata.
- Budget se zyada total ho to saaf bataya jata hai.

## Limits

- In stores ki koi public ordering API nahi hai, isliye Claude website ko browser se chalata hai. Site ka layout badle ya captcha aaye to Claude ruk kar aapko list de dega taki aap khud order kar sako.
- Stock, daam aur delivery fee aapke address par depend karte hain.
- Scheduled order tabhi chalega jab us waqt browser tool available ho aur store me login ho.

## Development

```bash
python -m unittest discover -s tests -v
```

Skill ki list ek hi file me rehti hai: `~/.rashan-order/list.json` (`RASHAN_DIR` se badal sakte ho). `.skill` file banane ke liye `rashan-order/` folder ko zip karke extension `.skill` rakh do, ya Claude ke skill-creator ka packager use karo.

## License

MIT
