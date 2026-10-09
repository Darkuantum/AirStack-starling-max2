# Starling 2 Max Propellers + Singapore Procurement/Logistics (ModalAI, Livox)

> Naming note up front: the product is officially **"Starling 2 Max"** (ModalAI), not "Starling Max 2".
> Searching the wrong word order is a real source of confusion — see the airframe-class section.

## Q1. What propellers does the Starling 2 Max ship with? (size, pitch, blades, material, bore/mount, CW/CCW, OEM part number, price)

### Takeaway
ModalAI publishes only **"180mm Tri-Blade"** / "180mm folding propellers" and sells them as a single SKU — **MRP-D0012-1-00, "Propellers, set of 4", US$29.99**. No pitch, material, bore diameter or hub thickness is published anywhere in ModalAI's docs or store, so the exact pitch and bore **must be measured on the actual aircraft** before ordering third-party equivalents.

### Cited Findings
- Datasheet lists propellers as **"180mm Tri-Blade"** and motors as **"2203.5 1500kv"**; ESC is the "ModalAI 4-in-1 Mini ESC" integrated with the power module — [ModalAI Starling 2 Max Datasheet](https://docs.modalai.com/starling-2-max-datasheet/)
- Hardware overview describes them as **"180mm folding propellers"** on a 322mm-diagonal carbon fibre airframe with 512mm prop-to-prop spacing — [ModalAI Starling 2 Max Hardware Overview](https://docs.modalai.com/starling-2-max-hardware-overview/)
- Airframe geometry (confirms prop diameter): diagonal 512mm prop-to-prop; motor-to-motor 260mm width x 190mm length (= 322mm motor diagonal); frame 3mm carbon fibre; take-off weight 566g; payload 500g — [Datasheet](https://docs.modalai.com/starling-2-max-datasheet/)
- Replacement-parts store page lists **"Propellers, set of 4" — $29.99 — MPN MRP-D0012-1-00**. The same page's included-parts list shows **"Propeller Nuts" (M10001405)** — [ModalAI Starling 2 Max Replacement Parts](https://www.modalai.com/products/starling-2-max-replacement-parts)
- The same page lists **two incompatible powertrain generations**: Motor V3 "original (gold)" **2203.5 1500kV, M10000073, $49.99** and Motor V4 "(black)" **2204 1500kV, M10001367, $49.99**; and two **non-interchangeable** carbon frames — V4 (M10001459, "wider motor mount spacing") and V1–V3 (M10000929, "smaller spacing"), both $249.99 — [ModalAI Starling 2 Max Replacement Parts](https://www.modalai.com/products/starling-2-max-replacement-parts)
- ModalAI staff confirmed the correct motor for the Starling MAX is the **2203.5 1500kv**, and that ModalAI customises the motor wire length for this model; the same thread notes the datasheet at one point listed 3000KV 1504 motors, which conflicts with the 1500kv motors actually fitted — [ModalAI forum post 20168](https://forum.modalai.com/post/20168)
- ModalAI staff: "the motor used on Starling 2 Max [is] very similar to Tmotor 2203.5 1500kv, you could also replace it with this one without changing any parameters" — [ModalAI forum (via search of forum threads on ESC/motor params)](https://forum.modalai.com/topic/5272/adding-payload-to-max2.md)
- **Wrong-part warning:** a customer with four Starling 2 Max drones bought **MPR-D0006-1-01 "Sentinel Replacement Propellers"** in Sept 2025 and they do **not** fit; ModalAI staff ("tom") redirected them to the Starling 2 Max replacement-parts page — [ModalAI forum post 23859](https://forum.modalai.com/post/23859), [forum post 23897](https://forum.modalai.com/post/23897)
- For the **original Starling 2** (not Max), staff pointed to a "Starling Propellers Set of 4" page; a user asked whether the original **4921 green** props are discontinued and whether **DJI 4726** is the recommended replacement — **ModalAI never answered** in that thread — [ModalAI forum topic 3819](https://forum.modalai.com/topic/3819/starling-2-replacement-propellers)
- Export/classification data on the replacement-parts page: **ECCN EAR99, HTS 8807.30 (aircraft parts), country of origin United States, RoHS compliant, "Active Production"** — [ModalAI Starling 2 Max Replacement Parts](https://www.modalai.com/products/starling-2-max-replacement-parts)

### Inferences
- 180mm = **7.09 inches**, so the stock prop is a **7-inch-class tri-blade**. The arithmetic is self-consistent: 322mm motor diagonal + 180mm prop diameter = 512mm prop-tip-to-prop-tip, exactly as the datasheet states. This is a strong cross-check that 180mm really is the prop *diameter*, not a blade length or a folded length.
- Because the store sells a separate **"Propeller Nuts" (M10001405)** line item, the mount is almost certainly a **threaded motor shaft with a prop nut**, not a press-fit/T-mount. Folding props in this class normally use an **aluminium hub clamped by the nut, with the blades on hub screws** — but ModalAI does not state this, so verify visually.
- The price works out to roughly **US$7.50 per propeller** from ModalAI, which is 2–3x the price of equivalent 7" tri-blades from an FPV shop (see Q4/Q5).
- The existence of V3 (T-Motor 2203.5 gold) vs V4 (ModalAI 2204 black) powertrains, plus two non-interchangeable frames, is directly relevant to this lab's **"two units of different hardware revisions"** — the prop SKU appears to be shared (one prop line item on the page), but shaft diameter should still be checked per airframe.

### Gaps
- **Pitch is not published anywhere.** No ModalAI doc, store page or forum post states the pitch of the 180mm tri-blade. Must be read off the prop hub (usually moulded, e.g. "7040-3") or measured.
- **Bore diameter / shaft diameter not published.** 7-inch-class folding props are typically M5 / 5mm bore, but ModalAI does not confirm this. Measure the motor shaft.
- **Hub thickness / centre thickness not published** by ModalAI.
- **Material not published** (glass-fibre nylon vs carbon-filled nylon vs PC).
- **CW/CCW split of the set of 4 is not stated** on the store page, nor is the rotation convention (PX4 quad-X default is CW on motors 1&2 / front-right & rear-left... but ModalAI does not document the prop labelling).
- **Manufacturer of the stock prop is not disclosed.** A ModalAI forum reply reportedly said they were still gathering the propeller manufacturer; I could not retrieve a later post confirming it (forum post 26487 returned 404 on fetch).
- **Weight per prop not published.**
- Whether the stock prop is genuinely *folding* (hinged blades) or a one-piece 180mm tri-blade is **internally inconsistent in ModalAI's own docs**: the datasheet says "180mm Tri-Blade", the hardware overview says "180mm folding propellers", the product page says "180 mm tri-blade". **Flag for physical inspection** — this single fact changes which third-party parts are candidates.

---

## Q2. Motors and rated prop sizes; airframe class; Starling vs Starling 2 vs Starling 2 Max confusion

### Takeaway
It is a **7-inch-class (322mm wheelbase) 4S quad on 2203.5/2204 1500kV motors** — unusually small stators for 7", which is deliberate: it is an efficiency/endurance airframe, not a freestyle one. The original Starling is a completely different, much smaller 120mm-prop machine, and conflating the two is the main sourcing trap.

### Cited Findings
- Starling 2 Max: motors **2203.5 1500kV** (V3/gold, T-Motor-equivalent) or **2204 1500kV** (V4/black, ModalAI) — [Datasheet](https://docs.modalai.com/starling-2-max-datasheet/); [Replacement Parts](https://www.modalai.com/products/starling-2-max-replacement-parts)
- Battery: **Sony VTC6 3000mAh 2S**, or any 2S 18650 Li-ion with XT30; **two 2S packs wired in series = 4S**; max voltage **16.8V** — [Datasheet](https://docs.modalai.com/starling-2-max-datasheet/)
- Take-off weight **566g**, payload capacity **500g** (flight time quoted at ~930g AUW) — [Datasheet](https://docs.modalai.com/starling-2-max-datasheet/)
- **Original Starling** (the small one): **1504 motors and 120mm propellers**; ModalAI sells a Starling-specific 1504 3000kV motor separately — [ModalAI Replacement Starling Motor](https://www.modalai.com/products/starling-replacement-motors); cross-referenced against [PX4 docs: ModalAI Starling](https://docs.px4.io/v1.17/en/complete_vehicles_mc/modalai_starling)
- A ModalAI forum user noted the Starling 2 Max datasheet at one point listed **3000KV 1504 motors**, which conflicted with the 1500kv motors actually on the aircraft — i.e. **ModalAI's own datasheet has carried Starling-vs-Starling-2-Max cross-contamination** — [ModalAI forum post 20168](https://forum.modalai.com/post/20168)
- **Sentinel** is a different ModalAI airframe with its own prop SKU (MPR-D0006-1-01) that does **not** fit the Starling 2 Max — [ModalAI forum post 23897](https://forum.modalai.com/post/23897)
- Starling 2 Max kit prices US$4,199.99 (K0, drone only, C28 cameras, WiFi+ELRS) up to US$6,799.99 (K3 with case, battery, wall PSU, controller). **"Expected to ship within 60 business days from San Diego, CA."** Export data: **ECCN EAR99, HTS 8806.22.0000, country of origin USA** — [ModalAI Starling 2 Max product page](https://www.modalai.com/products/starling-2-max)
- Spare propellers are **not included** in any kit (K0–K3) — [ModalAI Starling 2 Max product page](https://www.modalai.com/products/starling-2-max)

### Inferences
- 2203.5/2204 stators spinning 7" props at 1500kV on 4S is near the top of what those motors can take. Typical 7" FPV builds use **2806.5–2808** stators; Gemfan's own 7" prop listings recommend **2806.5 1350kV** or **"2808 and up"**. That means the stock prop is almost certainly a **low-pitch, low-load 7"** (likely 3.0–3.7" pitch class), chosen so the small motors are not overloaded. **Fitting a high-pitch or "freestyle" 7" prop on this aircraft is the single most likely way to cook the motors or ESC.**
- The four ModalAI airframes in circulation (Starling, Starling 2, Starling 2 Max, Sentinel) each have different props; because the store search is poor (a user reported the Starling prop page does not come up in shop search), **always order by MPN, via direct link.**
- 60 business days quoted lead time on the airframe suggests spares should be bought **well ahead of need** — treat props as a stocked consumable, not a just-in-time order.

### Gaps
- No published thrust stand data or manufacturer prop-rating for the 2203.5/2204 1500kV with a 7" prop, so "what prop sizes are these motors rated for" cannot be answered from a primary source. ModalAI only ever says "use the stock prop".

---

## Q3. Third-party compatibility: what must match, and the consequences of getting it wrong

### Takeaway
There is **no ModalAI-blessed third-party prop**. The closest dimensional matches on the open market are the **Gemfan 7-inch tri-blades** (178.8mm, M5 bore, ~7mm centre thickness, ~8–9g), and in particular the **Gemfan F7036 folding 3-blade** if the stock prop turns out to be a folder. Matching *diameter + bore + hub thickness* is necessary but not sufficient — pitch and weight are what determine whether the stock PX4/ESC tune still holds.

### Cited Findings (candidate parts, with real specs)
- **Gemfan F7036 folding 3-blade, set of 4** — prop disk diameter **177.8mm**, **3.6" pitch**, **5mm centre hole**, **8.2g**, glass-fibre nylon, **aluminium hub** folding design, max prop width 17.6mm, **centre thickness 7.25mm**, set contains 6 CW + 6 CCW blades plus 4 paddle clips and a hardware pack, recommended motor 2806.5 1350kV, **US$7.49/set of 4** — [RaceDayQuads: Gemfan F7036 Folding 3-Blade](https://racedayquads.com/products/gemfan-f7036-folding-3-blade-propeller-set-of-4-black)
- **Gemfan 7037-3 (non-folding tri-blade)** — **178.8mm** diameter, **3.7" pitch**, **8.7g**, reinforced carbon nylon, **centre thickness 7mm**, **M5 centre hole**, recommended motor "2808 and up", **US$3.49**, in stock at a Singapore-based shop — [OddityRC (Singapore): Gemfan 7037-3](https://oddityrc.com/products/gemfan-7037-3-carbon-nylon-for-cinelifter-macro-quad)
- Other 7" options at the same Singapore shop: **Gemfan 7035-2 Long Range US$3.29**, **Gemfan 7035-3 Freestyle US$3.49**, **Gemfan Flash 7040-3 US$2.99** — [OddityRC 7" props collection](https://oddityrc.com/collections/7-props)
- Gemfan F7036 is also available 2-blade (5.5g) as well as 3-blade (8.2g) — [RaceDayQuads: Gemfan F7036 Folding 2-Blade](https://racedayquads.com/products/gemfan-f7036-folding-2-blade-propeller-set-of-4-black)
- ModalAI staff on ESC parameters: "There is no need to re-calibrate the ModalAI ESC if you use a stock configuration, such as the motor + propeller that comes with Starling 2 MAX"; and "the ESC with the correct params is tuned for this motor + propeller and has been thoroughly tested, so I do not recommend trying to fix this by modifying ESC parameters" — [ModalAI forum, Starling 2 Max ESC/param threads](https://forum.modalai.com/post/19806)

### What must match (and the failure mode if it doesn't)
These are engineering consequences, derived from the cited specs — not quoted from a source:
- **Diameter (180mm / ~7.0–7.1")** — larger diameter raises thrust and current steeply (roughly with D^4 at fixed RPM) and risks tip-to-tip or tip-to-frame contact at 512mm prop-to-prop spacing. Smaller loses thrust and hover headroom. **Consequence: motor/ESC overheat, or loss of payload margin.**
- **Pitch** — the highest-leverage unknown. A 7040 (4.0") vs a 7035 (3.5") is ~14% more pitch, which on 2203.5 stators at 1500kV/4S means materially higher current and winding temperature at hover. **Consequence: hot motors, ESC desync/overheat, shortened endurance.** Do not go up in pitch from stock.
- **Bore / centre hole (M5 expected)** — wrong bore means it simply will not seat, or it seats off-centre. **Consequence: imbalance → high-frequency vibration → corrupted IMU → EKF innovation spikes and position/velocity estimate degradation, which for a mocap-fed EKF shows up as jitter and attitude-estimate noise even though position comes from OptiTrack.**
- **Hub / centre thickness (~7–7.25mm on the Gemfan 7" family)** — determines whether the prop nut has enough thread engagement. Too thin and the nut bottoms out on the shaft shoulder without clamping; too thick and there is not enough thread. **Consequence: prop departs in flight.**
- **Weight (8–9g for a 7" tri-blade)** — heavier props raise rotational inertia, which slows motor response and effectively de-tunes the PX4 rate loop (the stock gains become too hot for the new inertia). **Consequence: oscillation / "motor boating" on the rate loop.**
- **Blade count (3)** — going 2-blade raises efficiency and lowers current but changes thrust constant and sound signature; going 4-blade raises load. **Consequence: CA_ROTOR thrust/moment coefficients no longer describe the aircraft, so control allocation and hover throttle shift.**
- **CW/CCW mix** — obvious but worth stating: a folding-prop set ships as blade sets, and a mis-assembled folding hub (CW blades on a CCW hub) will flip instantly on takeoff.

### Inferences
- If the stock prop **is** folding, **Gemfan F7036 3-blade** is the closest off-the-shelf analogue (177.8mm vs 180mm, M5, 7.25mm centre, 8.2g). If it is **not** folding, **Gemfan 7035-3** or **7037-3** are the closest (178.8mm, M5, 7mm centre, 8.7g).
- Both candidate families carry a *manufacturer* motor recommendation of 2806.5–2808, i.e. **larger stators than the Starling 2 Max actually has**. This is not disqualifying (ModalAI clearly runs 7" on 2203.5 deliberately, at low AUW), but it means these props were not designed around this motor and current draw should be watched on the first flights.
- Buying generic 7" props as a consumable and keeping one set of genuine ModalAI props as the reference/"known-good" set is the sane approach for an indoor test lab.

### Gaps
- **No source confirms any third-party prop is a correct substitute for MRP-D0012-1-00.** Every third-party recommendation above is dimensional reasoning from published specs, not a ModalAI endorsement, and must be validated against the physical prop.
- I found **no Starling 2 Max thrust-stand or current-draw data** published by ModalAI or by users, so the current-draw consequences above cannot be quantified from sources.

---

## Q4. Does changing props require re-tuning PX4? Is there a ModalAI tuned parameter set tied to specific props?

### Takeaway
Yes, effectively. ModalAI ships a **tuned ESC parameter set and PX4 tune explicitly tied to the stock motor+prop combination**, tells users not to touch the ESC params while on stock hardware, and **explicitly declines to support tuning** for anything else — pointing users at the generic PX4 tuning guides.

### Cited Findings
- "There is no need to re-calibrate the ModalAI ESC if you use a stock configuration, such as the motor + propeller that comes with Starling 2 MAX" — ModalAI staff — [ModalAI forum](https://forum.modalai.com/post/19806)
- "the ESC with the correct params is tuned for this motor + propeller and has been thoroughly tested, so I do not recommend trying to fix this by modifying ESC parameters" — ModalAI staff — [ModalAI forum](https://forum.modalai.com/post/19806)
- On changing the aircraft's mass/configuration: "you will probably need to perform or at least check the Attitude Controller tuning, and Height Controller tuning (due to increased mass). Please consult the PX4 tuning guide(s) for this, **as we do not offer any additional information on that topic**" — and "you should be able to use a stock Starling 2 Max tune and make adjustments" — [ModalAI forum: adding payload to max2](https://forum.modalai.com/topic/5272/adding-payload-to-max2.md)
- A posted Starling 2 Max parameter dump contains per-rotor control-allocation entries including thrust coefficient **CA_ROTORn_CT** and moment coefficient **CA_ROTORn_KM** plus rotor positions (e.g. `CA_ROTOR1_PX : -0.0850`) — [ModalAI forum parameter dump](https://forum.modalai.com/post/26293)
- Replacing the motor with a T-Motor 2203.5 1500kv requires **no parameter change**, per ModalAI — [ModalAI forum](https://forum.modalai.com/topic/5272/adding-payload-to-max2.md)

### Inferences
- A **same-size, same-pitch, same-weight** prop swap (e.g. Gemfan 7035-3 for a stock 7035-class prop) should be flyable on the stock tune. A **different pitch or weight** changes the effective thrust constant, so `CA_ROTORn_CT` / hover throttle (`MPC_THR_HOVER`) and the rate-loop gains are the parameters most likely to need attention.
- For this lab specifically: because PX4 is fed OptiTrack position, a prop-induced vibration problem will not show as position drift first — it will show as **IMU vibration metrics and EKF innovation/variance** climbing, and as attitude-loop oscillation. Log `VIBE`/`estimator_innovations` on the first flight after any prop change.
- Practical sequence: baseline log on stock props → swap → hover with the stock tune → compare hover throttle, motor outputs, current, and vibration metrics → only then adjust.

### Gaps
- ModalAI publishes **no prop-specific parameter file** or "if you change props, change X" guidance. There is no documented mapping from prop SKU to parameter set.
- No source states whether `CA_ROTOR*_CT`/`KM` on the shipped Starling 2 Max airframe were measured for the stock prop or left at airframe-template defaults.

---

## Q5. Singapore sourcing — named shops, physical and online

### Takeaway
Singapore's FPV retail scene is thin but not empty: **OddityRC** is a genuine Singapore-registered FPV store (Paya Lebar Square) that **stocks four Gemfan 7-inch props at US$2.99–3.49 each** and offers local order pickup — that is the single best local match for this requirement. Beyond that, local sourcing drops to Carousell/Shopee/Lazada marketplace sellers and general RC shops that I could not verify stock 7" FPV props.

### Cited Findings
- **OddityRC** — Singapore address **"60 Paya Lebar Road, #11-53 Paya Lebar Square, 409051 Singapore"**; store region Singapore but **prices shown in USD**; has an **"Order Pickup Point"** at that address; free standard shipping on orders **>= US$99** (excl. BNF); "parts typically arrive in 5–8 days", BNF 7–12 days; contact oddityrc@gmail.com — [oddityrc.com](https://oddityrc.com/)
- OddityRC props catalogue covers Micro, 2", 2.5", 3", 3.5", 4", 5", 6", **7"**, 9" — [oddityrc.com](https://oddityrc.com/)
- OddityRC 7" stock, all Gemfan: **7035-2 Long Range US$3.29**, **7035-3 Freestyle US$3.49**, **7037-3 Cinelifter/Macro US$3.49**, **Flash 7040-3 US$2.99 (from US$3.69)** — [OddityRC 7" props](https://oddityrc.com/collections/7-props)
- OddityRC is the **only Singapore-based FPV store** in the DIYFPV store directory, which also says roughly **4 additional overseas FPV stores currently ship to Singapore** — [DIYFPV Singapore store directory](https://www.diyfpv.com/catalog/stores/singapore) (page returned HTTP 403 on direct fetch; content via search index — treat as indicative)
- **Helicopter Smartfly** — RC shop operating since 2010, retail store at **#02-04 Queensway Shopping Centre**, sells LiPo/Li-ion/NiCd/NiMH batteries and chargers; open Mon–Sat, **closed Wednesdays** — [business listing via search](https://www.diyfpv.com/catalog/stores/singapore). **Not verified to stock FPV propellers.**
- **DroneMatters** appears as a Singapore vendor in an (undated) community vendor list — [intofpv.com vendor list](https://intofpv.com/t-reliable-rc-parts-shops-vendors-world-wide). **Operating status unverified.**
- **Carousell SG** has active FPV categories with individual sellers (fpv-drone, brushless-motor, rc-drone-battery, analog-fpv searches all return live SG listings) — [carousell.sg FPV](https://www.carousell.sg/fpv-drone/q/)
- **Desertcart SG** lists drone parts into Singapore with "customs and taxes included in the price" — e.g. DJI Mavic 4 Pro props at **S$33** — [desertcart.sg](https://www.desertcart.sg/products/729332044-mavic-4-pro-propellers.md). This is a reshipper/marketplace, not an FPV specialist.

### Inferences
- At US$2.99–3.49 per prop from a Singapore shop vs **US$7.50/prop** equivalent from ModalAI, local Gemfan sourcing is roughly **half to one-third the cost** before shipping — meaningful when props are a consumable.
- OddityRC pricing in USD with a local pickup point suggests it operates as a small SG-registered Shopify store with local fulfilment; "5–8 days" is consistent with shipping from within the region rather than same-day local stock, so **confirm by email before relying on it for a same-week resupply.**
- None of OddityRC's four 7" props is described as **folding**. If the Starling 2 Max prop turns out to be a true folder, there is currently **no verified Singapore local source** and the F7036 would have to come from overseas (RaceDayQuads etc.) or a Shopee/Lazada/AliExpress seller.

### Gaps
- **I could not verify any Shopee SG or Lazada SG seller stocking 7-inch Gemfan props.** The web search tool used here is US-biased and returned no Shopee/Lazada SG results; these marketplaces are heavily JS-driven and not well indexed. Someone should search Shopee.sg and Lazada.sg directly for "Gemfan 7035" / "7 inch propeller" — this is a known-populated niche but I cannot cite a specific seller.
- No Singapore shop could be verified to stock the ModalAI OEM prop (MRP-D0012-1-00). Almost certainly none does — it is a ModalAI-direct part.
- **Hobby Bounties, Rotorgeeks** and other names in the SG RC scene returned nothing verifiable; I am not asserting they exist or stock these parts.
- OddityRC's stock *status* per SKU was not visible on the collection page (only the 7037-3 product page showed "in stock").

---

## Q6. Regional/international online stores that ship to Singapore

### Takeaway
I could **not verify Singapore shipping policies on the major US FPV retailers' own pages** within this research. What is verifiable is that a Singapore-local store (OddityRC) covers the Gemfan 7" range, and that a third-party directory says ~4 overseas FPV stores ship to Singapore.

### Cited Findings
- **RaceDayQuads** lists the Gemfan F7036 folding props at **US$7.49/set of 4 (3-blade)** and stock-available; **international shipping policy not stated on the product page** — [RaceDayQuads F7036 3-blade](https://racedayquads.com/products/gemfan-f7036-folding-3-blade-propeller-set-of-4-black)
- **GetFPV** is used by ModalAI staff themselves as a third-party parts source — staff linked a GetFPV XT60-to-XT30 adapter when ModalAI did not sell one — [ModalAI forum post 23859](https://forum.modalai.com/post/23859)
- **MyFPVStore** sells 2- through 8-blade props including the GemFan folding 7" 7036 range; **does not state whether it ships to Singapore** — [myfpvstore.com](https://www.myfpvstore.com/fuf9)
- **DIYFPV** directory states ~**4 overseas FPV stores currently ship to Singapore** and that its catalogue (1,100+ products) is synced daily with store price and stock — [DIYFPV Singapore](https://www.diyfpv.com/catalog/stores/singapore)
- **Pyrodrone** maintains a 7-inch prop category — [pyrodrone.com 7" props](https://pyrodrone.com/collections/all/propeller-size_7)

### Inferences
- The practical ranking for this lab: (1) OddityRC locally for non-folding Gemfan 7" consumables; (2) AliExpress/Banggood-class sellers for cheap bulk (shipping to SG is routine, 1–3 weeks, and SG's LVG GST is collected at checkout by registered platforms — see Q9); (3) RaceDayQuads/GetFPV for the folding F7036 if required, accepting US outbound freight; (4) ModalAI direct for the guaranteed-correct OEM part at 2–3x price.

### Gaps
- **No verified shipping cost or transit time to Singapore from GetFPV, RaceDayQuads, Pyrodrone or HobbyKing.** Their shipping pages were not retrievable in this pass. Do not state SG delivery times for these retailers without checking.
- I did not verify AliExpress/Banggood SG delivery times from a primary source; the claim above is an inference.

---

## Q7. Ordering ModalAI hardware into Singapore

### Takeaway
ModalAI sells **direct from San Diego with a worldwide country selector, all priced in USD**, publishes **no APAC distributor**, and quotes **60 business days** on a Starling 2 Max airframe (vs ~10 business days on most catalogue items). There is **no evidence of a Singapore or APAC reseller**.

### Cited Findings
- Starling 2 Max: **"Expected to ship within 60 business days from San Diego, CA"** — [ModalAI Starling 2 Max](https://www.modalai.com/products/starling-2-max)
- ModalAI says it **ships internationally** and that **most products ship within 10 business days**; it has stated it is **not currently shipping products to India due to customs difficulties**; technical questions go to the forum, monitored daily by ModalAI engineers — [ModalAI contact page](https://www.modalai.com/pages/beta-contact-us) (retrieved via search summary; direct fetch returned HTTP 429 — re-verify)
- Storefront defaults to "United States (USD $)" with a country selector offering many countries, **all priced in USD**; **no shipping rates, methods or delivery times are published**; "Each order ships the selected part only" — [ModalAI Starling 2 Max Replacement Parts](https://www.modalai.com/products/starling-2-max-replacement-parts)
- Export data published per SKU: **props/parts ECCN EAR99, HTS 8807.30, origin USA**; **complete aircraft ECCN EAR99, HTS 8806.22.0000, origin USA** — [Replacement Parts](https://www.modalai.com/products/starling-2-max-replacement-parts), [Starling 2 Max](https://www.modalai.com/products/starling-2-max)
- Dedicated searches for a ModalAI APAC reseller/distributor returned **nothing** — no partner directory, no regional distributor (results were all unrelated companies) — search performed 2026-10-08

### Inferences
- **"Each order ships the selected part only"** means ordering five different spares generates five shipments and five sets of international freight. For a Singapore lab, **consolidate into a single larger order** or you will pay freight repeatedly.
- **EAR99** is the practically important finding: these are **not ITAR / not USML** items (see Q9), so a US-origin ModalAI shipment to a Singapore research lab is an ordinary commercial export, not a licensed one.
- Absent a distributor, the realistic model is: ModalAI direct for airframe-specific parts (props, frames, motors, ESC), local/regional for generic consumables.

### Gaps
- **No carrier, freight cost, or SG transit time** is published by ModalAI, and I found **no forum thread from a Singapore customer** describing their experience with freight, duties or customs. This is a genuine hole — worth asking directly on forum.modalai.com, where ModalAI staff respond.
- No published ModalAI policy on who pays duties/GST (DDP vs DDU).
- Whether ModalAI's India restriction has since been lifted is unverified.

---

## Q8. Livox / DJI distribution into Singapore (Mid-360)

### Takeaway
I found **no authorised Livox distributor in Singapore**, and **no SGD price** for the Mid-360 anywhere. The nearest regional authorised channel I could identify is **Optimus Control in Kuala Lumpur, Malaysia**. Also important: the **original Mid-360 is being phased out in favour of the Mid-360S**, and a cheaper **Mid-360L** has been announced.

### Cited Findings
- **No Singapore Livox distributor found.** Repeated targeted searches returned only overseas sellers; Livox's own site has no retrievable "where to buy" / dealer page (livoxtech.com/dealer returns HTTP 404) — searches performed 2026-10-08
- **Optimus Control Industry (Kuala Lumpur / Selangor, Malaysia)** lists itself as a **supplier/distributor** of Livox MID-40 / MID-70 / **MID-360** compact 3D LiDAR — [optimuscontrol.com](https://www.optimuscontrol.com/showproducts/productid/5854251/cid/544490/livox-mid40-mid70-mid360-compact-3d-lidar-sensor/)
- **DJI Store Hong Kong** carries Livox product (Livox Avia listed), with after-sales directed to cs@livoxtech.com — [store.dji.com HK, Livox Avia](https://store.dji.com/cn/product/livox-avia?vid=99381)
- **Robotics Center (US)** describes itself as an **authorised distributor**, lists the Mid-360 at **US$899, on backorder**, shipping from San Francisco; no Singapore mention — [roboticscenter.ai](https://www.roboticscenter.ai/ar/store/product/livox-dji-livox-mid-360)
- **Robotopian** lists Mid-360/Mid-360S and its shipping FAQ **names Singapore among destinations**, with the caveat "if your country or region is not shown at checkout, please contact the Robotopian team" and "contact us before ordering to confirm availability"; Mid-360S listed ~**US$899** — [robotopian.com](https://robotopian.com/collections/livox-lidar)
- **Sonny Robotics** lists the Mid-360 at **US$852**, fulfilment "1–2 weeks" — [sonnyrobotics.com](https://sonnyrobotics.com/products/livox-mid-360)
- **OpenELAB** sells the MID-360S (ROS2 supported), seller address **Shenzhen, China**; one storefront shows a pre-sale "back in 3–4 weeks" — [openelab.io](https://openelab.io/products/livox-mid360)
- **Livox Tech Germany** lists MID-360S in stock at **€772.95 incl. 19% VAT + €25 shipping** — [livoxtech.de](https://livoxtech.de/en/products/mid-360.html)
- **CRK Photo Imaging (Australia)** lists the Mid-360S (100m range) at **$2,099.00** (presumed AUD) with an **ETA July 2026** — [crkphotoimaging.com.au](https://crkphotoimaging.com.au/products/livoxmid360s/livox-mid-360s-lidar---100m-range)
- **Product transition:** a reseller states "the original Livox MID-360 LiDAR is being phased out and stock may be limited", offering the MID-360S as the upgrade, improving "reliability, anti-interference capability, and system compatibility" — [robotopian.com](https://robotopian.com/collections/livox-lidar)
- **Livox Mid-360L** announced — a cheaper half-point-rate variant; **no price published** — [DroneXL, 2026-09-21](https://dronexl.co/2026/09/21/livox-mid-360l-lidar-half-point-rate-robots/)
- Livox list price reference point: Livox has listed the Mid-360 at **US$979**, noting tariffs can change the price; a 2023 launch "trial sample" price of **US$749** is obsolete — [livoxtech.com Mid-360 launch](https://www.livoxtech.com/news/mid360_launch)

### Inferences
- Expect roughly **US$850–980 (~S$1,100–1,300)** for a Mid-360/360S unit before freight and GST, with **1–4 weeks typical lead time**, and longer if the original Mid-360 is genuinely being run down.
- Because Livox is a DJI brand, DJI's regional retail/enterprise dealer network in Singapore is the most likely authorised route — but **I could not verify a named Singapore DJI dealer carrying Livox**, so this is a lead, not a finding.
- If buying the Mid-360 specifically (not the 360S), **buy now** — the phase-out claim comes from a reseller, but is consistent with the Mid-360S/360L product cadence.

### Gaps
- **No named Singapore dealer, no SGD price, no SG lead time** for Livox. This is the weakest-sourced part of the brief. Recommend contacting (a) Livox via livoxtech.com contact / cs@livoxtech.com asking for the Singapore partner, (b) Optimus Control in KL, and (c) DJI Enterprise's Singapore dealer list.
- Whether Mid-360 vs Mid-360S is ROS2/FAST-LIO drop-in compatible was not researched here (out of scope).

---

## Q9. Import friction: GST, customs, export control, CAAS

### Takeaway
Practically: **9% GST applies to essentially everything imported, with no useful de-minimis** since the Low-Value Goods regime took effect; ModalAI hardware is **EAR99 (not ITAR)**, so no US export licence issue for a Singapore civil research lab; and Singapore's Strategic Goods (Control) Act regulates **exports/transhipment, not imports** — imports just need the normal TradeNet permit.

### Cited Findings — GST
- GST on imported **low-value goods (<= S$400)** began at **8% on 1 Jan 2023** and rose to **9% on 1 Jan 2024**; it applies to goods imported via **air or post** from **GST-registered** overseas suppliers — [Sovos: Singapore updates Low Value Goods GST policy](https://sovos.com/en-gb/blog/vat/singapore-updates-low-value-goods-gst-policy)
- Sovos: the **S$400 threshold excludes transportation, insurance and duties** payable to Singapore Customs — [Sovos](https://sovos.com/en-gb/blog/vat/singapore-updates-low-value-goods-gst-policy); **contradicted by** Passport Global, which says the de-minimis is calculated on **CIF value** — [Passport Global](https://passportglobal.com/blog/2023-singapore-import-tax-changes); ZenMarket says it is the **value of the products, not the parcel** — [ZenMarket](https://zenmarket.jp/en/blog/post/12079/singapore-GST-pre-collection). **These three sources conflict; IRAS/Singapore Customs is the authority.**
- Orders **above S$400** have duty and tax **collected at customs clearance** rather than at checkout — [Passport Global](https://passportglobal.com/blog/2023-singapore-import-tax-changes)
- Overseas vendors must register for Singapore GST if LVG sales to SG consumers exceed **S$100,000/yr** and global turnover exceeds **S$1M** (single commercial-guide source — verify with IRAS) — [Passport Global](https://passportglobal.com/blog/2023-singapore-import-tax-changes)

### Cited Findings — customs / strategic goods
- Singapore Customs: the **Strategic Goods (Control) Act does not regulate the importation** of strategic goods; the Regulation of Imports and Exports Act still applies, and a **general TradeNet import permit is required prior to import** of any strategic good — [Singapore Customs: Strategic Goods Control](https://www.customs.gov.sg/permits-and-licences/trade-controls-and-prohibitions/strategic-goods-control/)
- The SGCA regulates **export, transhipment, transit, intangible technology transfer and brokering**, with a catch-all for WMD end-use; the control list was updated by the **Strategic Goods (Control) Order 2025, effective 1 Dec 2025** — [Singapore Customs](https://www.customs.gov.sg/businesses/strategic-goods-control-1/overview/legislation)
- Since **1 May 2019**, transhipment/transit exemptions were removed for specific codes under **"sensors and lasers", "navigation and avionics", and "aerospace and propulsion"** categories — [Singapore Customs](https://www.customs.gov.sg/permits-and-licences/trade-controls-and-prohibitions/strategic-goods-control/)
- Enforcement precedent: **Hydronav Services (Singapore) Pte Ltd fined S$1,133,412.25** for two counts of exporting strategic goods (reported to include a sonar system and a survey drone, to Myanmar) without permits, under s.5 SGCA — [WorldECR](https://www.worldecr.com/?p=2027273)
- A law-firm commentary reports a **Regulation of Imports and Exports (Amendment) Act published 13 April 2026**, expanding controlled items and enforcement powers — [Global Law Experts](https://globallawexperts.com/strategic-goods-control-singapore/). **Secondary source — verify officially.**

### Cited Findings — US export control
- ModalAI publishes **ECCN EAR99** on both the Starling 2 Max airframe and its replacement parts, with **country of origin USA** — [ModalAI Starling 2 Max](https://www.modalai.com/products/starling-2-max), [Replacement Parts](https://www.modalai.com/products/starling-2-max-replacement-parts)
- EAR99 means the item is **not on the US Munitions List (so not ITAR) and not on the Commerce Control List**, hence has no assigned ECCN — [Shipping Solutions: EAR99 isn't a free pass](https://shippingsolutionssoftware.com/blog/ear99-isnt-a-free-pass-for-export-compliance)
- EAR99 is **not an exemption from compliance**: depending on destination, recipient and end use, even EAR99 items can require a licence; exporters must still screen for embargoed destinations and denied parties — [Shipping Solutions](https://shippingsolutionssoftware.com/blog/ear99-isnt-a-free-pass-for-export-compliance)

### Inferences
- **Net effect for this lab:** expect **9% GST on every import regardless of value** — either collected at checkout by a registered platform (Shopee/Lazada/AliExpress/large US retailers) or at clearance by the courier (which usually adds a handling/disbursement fee). There is effectively no "under the threshold, no tax" option any more.
- **Singapore is not an embargoed destination and is not on US denied-party lists as a country**, so EAR99 ModalAI shipments to an SG research institute are routine commercial exports. The lab should still be prepared to answer a routine end-use question from ModalAI.
- **Chinese-origin Livox** carries no Singapore import restriction identified here, but note the **US** has had ongoing restrictions on DJI-affiliated entities; that is a concern only if the lab later ships Livox-equipped hardware *into* the US, not for importing into SG.
- The **re-export/transhipment** angle is the real risk for a Singapore lab: if the lab ever ships a Livox- or sensor-equipped drone *out* of Singapore, the SGCA "sensors and lasers" / "navigation and avionics" categories are live, and the Hydronav fine shows Customs enforces this. Importing for own use in Singapore does not trigger it.

### Gaps
- **No CAAS finding.** I found **no CAAS rule covering the import or purchase of drone spare parts or LiDAR**. CAAS regulates operation/registration of unmanned aircraft, not components, as far as these sources show — but I could not retrieve a CAAS page confirming this either way, so treat it as unverified rather than as a clean "no".
- Whether a specific Livox LiDAR falls under a controlled "sensors and lasers" code in the Strategic Goods Control Order 2025 was **not determined** — it needs the actual control-code lookup.
- The S$400 CIF-vs-goods-value question is genuinely contradicted across three secondary sources; IRAS is the authority and was not retrieved.
- No source found on how couriers (DHL/FedEx/UPS SG) actually handle duty/GST collection and handling fees for these specific categories.

---

## Cross-cutting: what the lab must physically measure before ordering anything

Flagged explicitly because ModalAI does not publish it:
1. **Read the moulding on the prop hub** — Gemfan/HQProp/Dalprop all mould the size code (e.g. "7035-3", "F7036") into the hub. This alone likely identifies the OEM part and resolves the pitch question.
2. **Is it folding or one-piece?** ModalAI's own docs contradict each other on this.
3. **Motor shaft diameter / prop bore** — expected M5, unconfirmed.
4. **Hub centre thickness** — expected ~7mm, unconfirmed.
5. **Prop weight on a scale** — expected 8–9g, unconfirmed.
6. **Which revision is each airframe** — V3 (gold T-Motor 2203.5) vs V4 (black ModalAI 2204), and V3 vs V4 carbon frame (different motor-mount spacing). The lab has two different revisions, and ModalAI states the frames are **not interchangeable**.
