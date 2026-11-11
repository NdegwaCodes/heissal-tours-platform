import { contact } from "@/lib/api";

export const metadata = {
  title: "Ocean and Altitude",
  description: "A twelve-night fixed itinerary from the Diani reef to the northern slopes of Mount Kenya.",
};

// Reproduced from the approved Claude Design itinerary artboard, with the
// Malindi photographs in its slots and a Key experiences section added.
const HTML = `<main data-dc-tpl="109">
    <section data-dc-tpl="110" style="padding: clamp(40px, 6vw, 72px) clamp(20px, 6vw, 88px) clamp(32px, 4vw, 48px);">
      <div data-dc-tpl="111" style="max-width: 1200px; margin: 0px auto;">
        <a href="/" data-dc-tpl="112" style="cursor: pointer; font-size: 12px; font-weight: 500; letter-spacing: 0.13em; text-transform: uppercase; color: rgb(107, 101, 88);" style="text-decoration:none">← Back</a>
        <div data-dc-tpl="113" style="font-size: 12px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63); margin-top: 34px;">Fixed itinerary · Coast &amp; highlands</div>
        <h1 data-dc-tpl="114" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 300; font-size: clamp(38px, 5.4vw, 68px); line-height: 1.06; letter-spacing: 0.01em; margin: 16px 0px 0px; max-width: 18ch; text-wrap: pretty;">Ocean and Altitude</h1>
        <p data-dc-tpl="115" style="font-size: 18px; line-height: 1.65; color: rgb(107, 101, 88); max-width: 52ch; margin: 20px 0px 0px;">Twelve nights from the reef at Diani to the northern slopes of Mount Kenya — the two Kenyas most travellers only see one of.</p>
        <div data-dc-tpl="116" style="display: flex; gap: clamp(24px, 4vw, 56px); flex-wrap: wrap; margin-top: 36px; padding-top: 22px; border-top: 1px solid rgb(222, 214, 198);">
          <div data-dc-tpl="117">
            <div data-dc-tpl="118" style="font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63); font-weight: 500;">Length</div>
            <div data-dc-tpl="119" style="font-size: 16px; margin-top: 8px;">12 nights</div>
          </div>
          <div data-dc-tpl="120">
            <div data-dc-tpl="121" style="font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63); font-weight: 500;">Route</div>
            <div data-dc-tpl="122" style="font-size: 16px; margin-top: 8px;">Diani → Watamu → Nanyuki</div>
          </div>
          <div data-dc-tpl="123">
            <div data-dc-tpl="124" style="font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63); font-weight: 500;">Best months</div>
            <div data-dc-tpl="125" style="font-size: 16px; margin-top: 8px;">Jul–Oct, Jan–Mar</div>
          </div>
          <div data-dc-tpl="126">
            <div data-dc-tpl="127" style="font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63); font-weight: 500;">Indicative</div>
            <div data-dc-tpl="128" style="font-size: 16px; margin-top: 8px;"><span class="sc-interp">from $9,400 pp</span></div>
          </div>
        </div>
      </div>
    </section>

    <div data-dc-tpl="129" style="height: clamp(320px, 52vw, 620px); width: 100%;">
      <img src="/malindi/dhow.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
    </div>

    <section data-dc-tpl="131" style="padding: clamp(56px, 7vw, 96px) clamp(20px, 6vw, 88px);">
      <div data-dc-tpl="132" style="max-width: 1200px; margin: 0px auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: clamp(32px, 5vw, 72px); align-items: start;">
        <div data-dc-tpl="133">
          <h2 data-dc-tpl="134" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 300; font-size: clamp(28px, 3.2vw, 38px); line-height: 1.15; margin: 0px; max-width: 22ch; text-wrap: pretty;">The shape of the trip</h2>
          <p data-dc-tpl="135" style="font-size: 17px; line-height: 1.75; color: rgb(107, 101, 88); max-width: 62ch; margin: 20px 0px 0px;">You begin at sea level. Five nights on the south coast, where the reef sits close enough to swim to and the tide sets the day's timetable. Then north to Watamu for the creek, the ruins at Gede and a quieter stretch of sand.</p>
          <p data-dc-tpl="136" style="font-size: 17px; line-height: 1.75; color: rgb(107, 101, 88); max-width: 62ch; margin: 16px 0px 0px;">A short flight inland changes everything: 1,950 metres at Nanyuki, cold mornings, and Mount Kenya over the shoulder of the plains. The last four nights are spent on a conservancy, with game drives before breakfast and nothing scheduled after four.</p>
          <div data-dc-tpl="137" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-top: 36px;">
            <div data-dc-tpl="138" style="height: clamp(200px, 22vw, 260px); overflow: hidden; border-radius: 12px;">
              <img src="/malindi/shallows.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
            </div>
            <div data-dc-tpl="140" style="height: clamp(200px, 22vw, 260px); overflow: hidden; border-radius: 12px;">
              <img src="/malindi/mangroves.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
            </div>
          </div>
        </div>
        <aside data-dc-tpl="142" style="border: 1px solid rgb(222, 214, 198); padding: clamp(24px, 3vw, 34px); position: sticky; top: 110px; background: rgb(252, 249, 242); border-radius: 16px; box-shadow: 0 10px 30px rgba(16, 14, 11, 0.06);">
          <div data-dc-tpl="143" style="font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63); font-weight: 500;">Indicative price</div>
          <div data-dc-tpl="144" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-size: 34px; font-weight: 400; line-height: 1.1; margin-top: 10px;"><span class="sc-interp">from $9,400 pp</span></div>
          <p data-dc-tpl="145" style="font-size: 14px; line-height: 1.65; color: rgb(107, 101, 88); margin: 12px 0px 0px;">Based on two sharing, high season. Your quote is built from live property rates before you commit to anything.</p>
          <a href="/enquire" data-dc-tpl="146" class="scp1" style="cursor: pointer; background: rgb(28, 26, 23); color: rgb(247, 243, 236); padding: 16px 20px; text-align: center; font-size: 12px; font-weight: 500; letter-spacing: 0.13em; text-transform: uppercase; margin-top: 24px; border-radius: 8px;" style="text-decoration:none">Enquire about this trip</a>
          <div data-dc-tpl="147" style="font-size: 14px; color: rgb(107, 101, 88); line-height: 1.7; margin-top: 16px;">WhatsApp <span class="sc-interp">+254 700 000 000</span></div>
        </aside>
      </div>
    </section>

    <section data-dc-tpl="148" style="padding: 0px clamp(20px, 6vw, 88px) clamp(56px, 7vw, 96px);">
<div style="font-size:11px;font-weight:500;letter-spacing:0.14em;text-transform:uppercase;color:rgb(150,112,63);">Key experiences</div><h2 style="font-family:&quot;Cormorant Garamond&quot;,Georgia,serif;font-weight:300;font-size:clamp(28px,3.2vw,38px);line-height:1.15;margin:12px 0 0;max-width:24ch;">What you will remember</h2><div style="margin-top:24px;display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:0 44px;"><div style="display:flex;gap:12px;padding:14px 0;border-top:1px solid rgb(222,214,198);"><span style="color:rgb(150,112,63);">&mdash;</span><span style="font-size:15px;line-height:1.6;color:rgb(28,26,23);">Snorkel the Chale reef at slack tide</span></div><div style="display:flex;gap:12px;padding:14px 0;border-top:1px solid rgb(222,214,198);"><span style="color:rgb(150,112,63);">&mdash;</span><span style="font-size:15px;line-height:1.6;color:rgb(28,26,23);">A dhow sunset off the Watamu creek</span></div><div style="display:flex;gap:12px;padding:14px 0;border-top:1px solid rgb(222,214,198);"><span style="color:rgb(150,112,63);">&mdash;</span><span style="font-size:15px;line-height:1.6;color:rgb(28,26,23);">Gede ruins and the Mida Creek boardwalk</span></div><div style="display:flex;gap:12px;padding:14px 0;border-top:1px solid rgb(222,214,198);"><span style="color:rgb(150,112,63);">&mdash;</span><span style="font-size:15px;line-height:1.6;color:rgb(28,26,23);">Game drives on a private Laikipia conservancy</span></div><div style="display:flex;gap:12px;padding:14px 0;border-top:1px solid rgb(222,214,198);"><span style="color:rgb(150,112,63);">&mdash;</span><span style="font-size:15px;line-height:1.6;color:rgb(28,26,23);">Mount Kenya&rsquo;s northern slopes at first light</span></div><div style="display:flex;gap:12px;padding:14px 0;border-top:1px solid rgb(222,214,198);"><span style="color:rgb(150,112,63);">&mdash;</span><span style="font-size:15px;line-height:1.6;color:rgb(28,26,23);">Sundowners above the Ewaso Ng&rsquo;iro</span></div></div></section>
<section data-dc-tpl="148" style="padding: 0px clamp(20px, 6vw, 88px) clamp(56px, 7vw, 96px);">
      <div data-dc-tpl="149" style="max-width: 1200px; margin: 0px auto;">
        <h2 data-dc-tpl="150" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 300; font-size: clamp(28px, 3.2vw, 38px); line-height: 1.15; margin: 0px 0px clamp(28px, 3.4vw, 44px);">Day by day</h2>
        
          <div data-dc-tpl="152" style="display: grid; grid-template-columns: minmax(0px, 180px) minmax(0px, 1fr); gap: clamp(16px, 3vw, 48px); padding: 26px 0px; border-top: 1px solid rgb(222, 214, 198);">
            <div data-dc-tpl="153" style="font-size: 12px; font-weight: 500; letter-spacing: 0.13em; text-transform: uppercase; color: rgb(150, 112, 63);"><span class="sc-interp">Days 1–2</span></div>
            <div data-dc-tpl="154">
              <h3 data-dc-tpl="155" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 24px; line-height: 1.2; margin: 0px;"><span class="sc-interp">Arrive Diani</span></h3>
              <p data-dc-tpl="156" style="font-size: 16px; line-height: 1.75; color: rgb(107, 101, 88); max-width: 62ch; margin: 10px 0px 0px;"><span class="sc-interp">Met at Mombasa, an hour south by road and ferry. Nothing planned beyond finding the water.</span></p>
            </div>
          </div>
        
          <div data-dc-tpl="152" style="display: grid; grid-template-columns: minmax(0px, 180px) minmax(0px, 1fr); gap: clamp(16px, 3vw, 48px); padding: 26px 0px; border-top: 1px solid rgb(222, 214, 198);">
            <div data-dc-tpl="153" style="font-size: 12px; font-weight: 500; letter-spacing: 0.13em; text-transform: uppercase; color: rgb(150, 112, 63);"><span class="sc-interp">Days 3–5</span></div>
            <div data-dc-tpl="154">
              <h3 data-dc-tpl="155" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 24px; line-height: 1.2; margin: 0px;"><span class="sc-interp">Chale and the reef</span></h3>
              <p data-dc-tpl="156" style="font-size: 16px; line-height: 1.75; color: rgb(107, 101, 88); max-width: 62ch; margin: 10px 0px 0px;"><span class="sc-interp">Snorkelling on the drop-off, a dhow morning, and the tide deciding the rest. Kitesurfing between June and September.</span></p>
            </div>
          </div>
        
          <div data-dc-tpl="152" style="display: grid; grid-template-columns: minmax(0px, 180px) minmax(0px, 1fr); gap: clamp(16px, 3vw, 48px); padding: 26px 0px; border-top: 1px solid rgb(222, 214, 198);">
            <div data-dc-tpl="153" style="font-size: 12px; font-weight: 500; letter-spacing: 0.13em; text-transform: uppercase; color: rgb(150, 112, 63);"><span class="sc-interp">Days 6–7</span></div>
            <div data-dc-tpl="154">
              <h3 data-dc-tpl="155" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 24px; line-height: 1.2; margin: 0px;"><span class="sc-interp">North to Watamu</span></h3>
              <p data-dc-tpl="156" style="font-size: 16px; line-height: 1.75; color: rgb(107, 101, 88); max-width: 62ch; margin: 10px 0px 0px;"><span class="sc-interp">Mida Creek at low tide and the Gede ruins in the forest. Quieter sand, fewer people, better seafood.</span></p>
            </div>
          </div>
        
          <div data-dc-tpl="152" style="display: grid; grid-template-columns: minmax(0px, 180px) minmax(0px, 1fr); gap: clamp(16px, 3vw, 48px); padding: 26px 0px; border-top: 1px solid rgb(222, 214, 198);">
            <div data-dc-tpl="153" style="font-size: 12px; font-weight: 500; letter-spacing: 0.13em; text-transform: uppercase; color: rgb(150, 112, 63);"><span class="sc-interp">Days 8–9</span></div>
            <div data-dc-tpl="154">
              <h3 data-dc-tpl="155" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 24px; line-height: 1.2; margin: 0px;"><span class="sc-interp">Inland to Nanyuki</span></h3>
              <p data-dc-tpl="156" style="font-size: 16px; line-height: 1.75; color: rgb(107, 101, 88); max-width: 62ch; margin: 10px 0px 0px;"><span class="sc-interp">A short flight to 1,950 metres. Cold mornings, a fire in the evening, and the mountain in view.</span></p>
            </div>
          </div>
        
          <div data-dc-tpl="152" style="display: grid; grid-template-columns: minmax(0px, 180px) minmax(0px, 1fr); gap: clamp(16px, 3vw, 48px); padding: 26px 0px; border-top: 1px solid rgb(222, 214, 198);">
            <div data-dc-tpl="153" style="font-size: 12px; font-weight: 500; letter-spacing: 0.13em; text-transform: uppercase; color: rgb(150, 112, 63);"><span class="sc-interp">Days 10–11</span></div>
            <div data-dc-tpl="154">
              <h3 data-dc-tpl="155" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 24px; line-height: 1.2; margin: 0px;"><span class="sc-interp">Conservancy days</span></h3>
              <p data-dc-tpl="156" style="font-size: 16px; line-height: 1.75; color: rgb(107, 101, 88); max-width: 62ch; margin: 10px 0px 0px;"><span class="sc-interp">Game drives before breakfast on private land, walking with a guide, and afternoons left alone.</span></p>
            </div>
          </div>
        
          <div data-dc-tpl="152" style="display: grid; grid-template-columns: minmax(0px, 180px) minmax(0px, 1fr); gap: clamp(16px, 3vw, 48px); padding: 26px 0px; border-top: 1px solid rgb(222, 214, 198);">
            <div data-dc-tpl="153" style="font-size: 12px; font-weight: 500; letter-spacing: 0.13em; text-transform: uppercase; color: rgb(150, 112, 63);"><span class="sc-interp">Day 12</span></div>
            <div data-dc-tpl="154">
              <h3 data-dc-tpl="155" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 24px; line-height: 1.2; margin: 0px;"><span class="sc-interp">Nairobi and out</span></h3>
              <p data-dc-tpl="156" style="font-size: 16px; line-height: 1.75; color: rgb(107, 101, 88); max-width: 62ch; margin: 10px 0px 0px;"><span class="sc-interp">Back to the city with time for one last thing, then your flight home.</span></p>
            </div>
          </div>
        
      </div>
    </section>

    <section data-dc-tpl="157" style="padding: 0px clamp(20px, 6vw, 88px) clamp(72px, 9vw, 120px);">
      <div data-dc-tpl="158" style="max-width: 1200px; margin: 0px auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: clamp(32px, 5vw, 64px);">
        <div data-dc-tpl="159">
          <div data-dc-tpl="160" style="font-size: 12px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63);">Included</div>
          <div data-dc-tpl="161" style="display: flex; flex-direction: column; gap: 12px; margin-top: 18px;">
            
              <div data-dc-tpl="163" style="font-size: 16px; line-height: 1.6; padding-bottom: 12px; border-bottom: 1px solid rgb(222, 214, 198);"><span class="sc-interp">Accommodation in hand-picked properties throughout</span></div>
            
              <div data-dc-tpl="163" style="font-size: 16px; line-height: 1.6; padding-bottom: 12px; border-bottom: 1px solid rgb(222, 214, 198);"><span class="sc-interp">Private vehicle and driver-guide</span></div>
            
              <div data-dc-tpl="163" style="font-size: 16px; line-height: 1.6; padding-bottom: 12px; border-bottom: 1px solid rgb(222, 214, 198);"><span class="sc-interp">Domestic flights Diani–Nairobi–Nanyuki</span></div>
            
              <div data-dc-tpl="163" style="font-size: 16px; line-height: 1.6; padding-bottom: 12px; border-bottom: 1px solid rgb(222, 214, 198);"><span class="sc-interp">Park and conservancy fees</span></div>
            
              <div data-dc-tpl="163" style="font-size: 16px; line-height: 1.6; padding-bottom: 12px; border-bottom: 1px solid rgb(222, 214, 198);"><span class="sc-interp">Breakfast daily, full board on safari</span></div>
            
          </div>
        </div>
        <div data-dc-tpl="164">
          <div data-dc-tpl="165" style="font-size: 12px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63);">Not included</div>
          <div data-dc-tpl="166" style="display: flex; flex-direction: column; gap: 12px; margin-top: 18px;">
            
              <div data-dc-tpl="168" style="font-size: 16px; line-height: 1.6; color: rgb(107, 101, 88); padding-bottom: 12px; border-bottom: 1px solid rgb(222, 214, 198);"><span class="sc-interp">International flights</span></div>
            
              <div data-dc-tpl="168" style="font-size: 16px; line-height: 1.6; color: rgb(107, 101, 88); padding-bottom: 12px; border-bottom: 1px solid rgb(222, 214, 198);"><span class="sc-interp">Visas and travel insurance</span></div>
            
              <div data-dc-tpl="168" style="font-size: 16px; line-height: 1.6; color: rgb(107, 101, 88); padding-bottom: 12px; border-bottom: 1px solid rgb(222, 214, 198);"><span class="sc-interp">Personal spend and gratuities</span></div>
            
          </div>
        </div>
      </div>
    </section>

    <section data-dc-tpl="169" style="background: rgb(30, 71, 65); padding: clamp(64px, 8vw, 104px) clamp(20px, 6vw, 88px);">
      <div data-dc-tpl="170" style="max-width: 1200px; margin: 0px auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: clamp(32px, 5vw, 64px); align-items: center;">
        <h2 data-dc-tpl="171" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 300; font-size: clamp(28px, 3.6vw, 44px); line-height: 1.14; color: rgb(253, 251, 246); margin: 0px; max-width: 22ch; text-wrap: pretty;">Move a night, change a lodge, add the Mara</h2>
        <div data-dc-tpl="172" style="display: flex; flex-direction: column; gap: 18px; align-items: flex-start;">
          <p data-dc-tpl="173" style="font-size: 17px; line-height: 1.7; color: rgb(220, 231, 226); max-width: 42ch; margin: 0px;">This itinerary is a starting point. Tell us what you would change and we will price the version you actually want.</p>
          <a href="/enquire" data-dc-tpl="174" class="scp2" style="cursor: pointer; background: rgb(247, 243, 236); color: rgb(28, 26, 23); padding: 18px 36px; font-size: 12px; font-weight: 500; letter-spacing: 0.13em; text-transform: uppercase; border-radius: 8px;" style="text-decoration:none">Start an enquiry</a>
        </div>
      </div>
    </section>
  </main>`;

export default async function Itinerary() {
  // Same substitution as the home page (src/app/page.tsx) and for the same
  // reason: the design import's WhatsApp number is a placeholder, not this
  // business's real one.
  const info = await contact();
  const html = HTML.replace(/\+254 700 000 000/g, info.contact_phone || "+254 700 000 000");
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}
