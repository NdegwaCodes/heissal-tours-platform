import { Hero } from "@/components/hero";
import { contact } from "@/lib/api";
import { canonical, SITE_TAGLINE } from "@/lib/site";

export const metadata = {
  description: SITE_TAGLINE,
  alternates: { canonical: canonical("/") },
};

// The hero is now a real component (src/components/hero.tsx) in the modern
// language; the sections below are still the approved Claude Design artboard,
// restyled in place and rolled into the new look page by page.
const HTML = `

    <section id="itineraries" data-dc-tpl="29" style="padding: clamp(72px, 9vw, 132px) clamp(20px, 6vw, 88px) clamp(40px, 5vw, 64px);">
      <div data-dc-tpl="30" style="max-width: 1200px; margin: 0px auto;">
        <div data-dc-tpl="31" style="display: flex; align-items: flex-end; justify-content: space-between; gap: 32px; flex-wrap: wrap;">
          <div data-dc-tpl="32">
            <div data-dc-tpl="33" style="font-size: 12px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63);">Ready-made itineraries</div>
            <h2 data-dc-tpl="34" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 300; font-size: clamp(30px, 3.6vw, 42px); line-height: 1.15; letter-spacing: 0.01em; margin: 14px 0px 0px; max-width: 24ch; text-wrap: pretty;">Start from one of ours, or start from nothing</h2>
          </div>
          <p data-dc-tpl="35" style="font-size: 17px; line-height: 1.7; color: rgb(107, 101, 88); max-width: 38ch; margin: 0px;">Each of these is a trip we run and would take ourselves. Any of them can be moved, shortened or rebuilt around you.</p>
        </div>
      </div>
    </section>

    <section data-dc-tpl="36" style="padding: 0px clamp(20px, 6vw, 88px) clamp(72px, 9vw, 120px);">
      <div data-dc-tpl="37" style="max-width: 1200px; margin: 0px auto;">
        
          <div style="margin-top:6px;margin-bottom:26px;"><a href="/builder" style="font-size:12px;font-weight:500;letter-spacing:0.14em;text-transform:uppercase;color:rgb(150,112,63);text-decoration:none;border-bottom:1px solid rgb(150,112,63);padding-bottom:3px;">Or build your own trip &rarr;</a></div><div data-dc-tpl="39" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: clamp(20px, 2.6vw, 34px);">
            
              <a href="/itineraries/ocean-and-altitude" data-dc-tpl="41" class="sc-card" style="cursor: pointer; display: flex; flex-direction: column; text-decoration:none; color:inherit;">
                <div data-dc-tpl="42" style="height: clamp(240px, 26vw, 320px); width: 100%; overflow: hidden; border-radius: 14px;">
                  <img src="/malindi/shallows.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
                </div>
                <div data-dc-tpl="44" style="padding: 20px 2px 0px;">
                  <div data-dc-tpl="45" style="font-size: 11px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63);"><span class="sc-interp">Coast · Diani</span></div>
                  <h3 data-dc-tpl="46" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 25px; line-height: 1.2; margin: 10px 0px 0px; text-wrap: pretty;"><span class="sc-interp">The Chale Reef</span></h3>
                  <p data-dc-tpl="47" style="font-size: 15px; line-height: 1.65; color: rgb(107, 101, 88); margin: 10px 0px 0px;"><span class="sc-interp">Five minutes from the reef edge, with a dhow on standby and nothing on the calendar.</span></p>
                  <div data-dc-tpl="48" style="display: flex; align-items: center; gap: 12px; margin-top: 16px; padding-top: 14px; border-top: 1px solid rgb(222, 214, 198); font-size: 13px; color: rgb(28, 26, 23);">
                    <span data-dc-tpl="49"><span class="sc-interp">7 nights</span></span>
                    <span data-dc-tpl="50" style="color: rgb(201, 191, 169);">/</span>
                    <span data-dc-tpl="51" style="color: rgb(107, 101, 88);"><span class="sc-interp">from $4,850 pp</span></span>
                  </div>
                </div>
              </a>
            
              <a href="/itineraries/ocean-and-altitude" data-dc-tpl="41" class="sc-card" style="cursor: pointer; display: flex; flex-direction: column; text-decoration:none; color:inherit;">
                <div data-dc-tpl="42" style="height: clamp(240px, 26vw, 320px); width: 100%; overflow: hidden; border-radius: 14px;">
                  <img src="/malindi/harbour.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
                </div>
                <div data-dc-tpl="44" style="padding: 20px 2px 0px;">
                  <div data-dc-tpl="45" style="font-size: 11px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63);"><span class="sc-interp">Highlands · Nanyuki</span></div>
                  <h3 data-dc-tpl="46" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 25px; line-height: 1.2; margin: 10px 0px 0px; text-wrap: pretty;"><span class="sc-interp">Mount Kenya &amp; Laikipia</span></h3>
                  <p data-dc-tpl="47" style="font-size: 15px; line-height: 1.65; color: rgb(107, 101, 88); margin: 10px 0px 0px;"><span class="sc-interp">Conservancy game drives at 1,950m, with the mountain visible from breakfast.</span></p>
                  <div data-dc-tpl="48" style="display: flex; align-items: center; gap: 12px; margin-top: 16px; padding-top: 14px; border-top: 1px solid rgb(222, 214, 198); font-size: 13px; color: rgb(28, 26, 23);">
                    <span data-dc-tpl="49"><span class="sc-interp">8 nights</span></span>
                    <span data-dc-tpl="50" style="color: rgb(201, 191, 169);">/</span>
                    <span data-dc-tpl="51" style="color: rgb(107, 101, 88);"><span class="sc-interp">from $6,200 pp</span></span>
                  </div>
                </div>
              </a>
            
              <a href="/itineraries/ocean-and-altitude" data-dc-tpl="41" class="sc-card" style="cursor: pointer; display: flex; flex-direction: column; text-decoration:none; color:inherit;">
                <div data-dc-tpl="42" style="height: clamp(240px, 26vw, 320px); width: 100%; overflow: hidden; border-radius: 14px;">
                  <img src="/malindi/mangroves.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
                </div>
                <div data-dc-tpl="44" style="padding: 20px 2px 0px;">
                  <div data-dc-tpl="45" style="font-size: 11px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63);"><span class="sc-interp">Coast · Watamu</span></div>
                  <h3 data-dc-tpl="46" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 25px; line-height: 1.2; margin: 10px 0px 0px; text-wrap: pretty;"><span class="sc-interp">Watamu &amp; the Dhow Coast</span></h3>
                  <p data-dc-tpl="47" style="font-size: 15px; line-height: 1.65; color: rgb(107, 101, 88); margin: 10px 0px 0px;"><span class="sc-interp">Mida Creek at low tide, the Gede ruins, and the emptiest sand on the coast.</span></p>
                  <div data-dc-tpl="48" style="display: flex; align-items: center; gap: 12px; margin-top: 16px; padding-top: 14px; border-top: 1px solid rgb(222, 214, 198); font-size: 13px; color: rgb(28, 26, 23);">
                    <span data-dc-tpl="49"><span class="sc-interp">6 nights</span></span>
                    <span data-dc-tpl="50" style="color: rgb(201, 191, 169);">/</span>
                    <span data-dc-tpl="51" style="color: rgb(107, 101, 88);"><span class="sc-interp">from $4,200 pp</span></span>
                  </div>
                </div>
              </a>
            
              <a href="/itineraries/ocean-and-altitude" data-dc-tpl="41" class="sc-card" style="cursor: pointer; display: flex; flex-direction: column; text-decoration:none; color:inherit;">
                <div data-dc-tpl="42" style="height: clamp(240px, 26vw, 320px); width: 100%; overflow: hidden; border-radius: 14px;">
                  <img src="/malindi/dhow.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
                </div>
                <div data-dc-tpl="44" style="padding: 20px 2px 0px;">
                  <div data-dc-tpl="45" style="font-size: 11px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63);"><span class="sc-interp">Coast &amp; highlands</span></div>
                  <h3 data-dc-tpl="46" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 25px; line-height: 1.2; margin: 10px 0px 0px; text-wrap: pretty;"><span class="sc-interp">Ocean and Altitude</span></h3>
                  <p data-dc-tpl="47" style="font-size: 15px; line-height: 1.65; color: rgb(107, 101, 88); margin: 10px 0px 0px;"><span class="sc-interp">The full arc: sea level to the northern slopes, one country, two climates.</span></p>
                  <div data-dc-tpl="48" style="display: flex; align-items: center; gap: 12px; margin-top: 16px; padding-top: 14px; border-top: 1px solid rgb(222, 214, 198); font-size: 13px; color: rgb(28, 26, 23);">
                    <span data-dc-tpl="49"><span class="sc-interp">12 nights</span></span>
                    <span data-dc-tpl="50" style="color: rgb(201, 191, 169);">/</span>
                    <span data-dc-tpl="51" style="color: rgb(107, 101, 88);"><span class="sc-interp">from $9,400 pp</span></span>
                  </div>
                </div>
              </a>
            
              <a href="/itineraries/ocean-and-altitude" data-dc-tpl="41" class="sc-card" style="cursor: pointer; display: flex; flex-direction: column; text-decoration:none; color:inherit;">
                <div data-dc-tpl="42" style="height: clamp(240px, 26vw, 320px); width: 100%; overflow: hidden; border-radius: 14px;">
                  <img src="/malindi/ocean-safari.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
                </div>
                <div data-dc-tpl="44" style="padding: 20px 2px 0px;">
                  <div data-dc-tpl="45" style="font-size: 11px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63);"><span class="sc-interp">Coast · Lamu</span></div>
                  <h3 data-dc-tpl="46" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 25px; line-height: 1.2; margin: 10px 0px 0px; text-wrap: pretty;"><span class="sc-interp">Lamu, Under Sail</span></h3>
                  <p data-dc-tpl="47" style="font-size: 15px; line-height: 1.65; color: rgb(107, 101, 88); margin: 10px 0px 0px;"><span class="sc-interp">Coral-stone lanes, no cars, and a dhow that leaves when the tide decides.</span></p>
                  <div data-dc-tpl="48" style="display: flex; align-items: center; gap: 12px; margin-top: 16px; padding-top: 14px; border-top: 1px solid rgb(222, 214, 198); font-size: 13px; color: rgb(28, 26, 23);">
                    <span data-dc-tpl="49"><span class="sc-interp">5 nights</span></span>
                    <span data-dc-tpl="50" style="color: rgb(201, 191, 169);">/</span>
                    <span data-dc-tpl="51" style="color: rgb(107, 101, 88);"><span class="sc-interp">from $3,900 pp</span></span>
                  </div>
                </div>
              </a>
            
              <a href="/itineraries/ocean-and-altitude" data-dc-tpl="41" class="sc-card" style="cursor: pointer; display: flex; flex-direction: column; text-decoration:none; color:inherit;">
                <div data-dc-tpl="42" style="height: clamp(240px, 26vw, 320px); width: 100%; overflow: hidden; border-radius: 14px;">
                  <img src="/malindi/sunset.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
                </div>
                <div data-dc-tpl="44" style="padding: 20px 2px 0px;">
                  <div data-dc-tpl="45" style="font-size: 11px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63);"><span class="sc-interp">Masai Mara</span></div>
                  <h3 data-dc-tpl="46" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 25px; line-height: 1.2; margin: 10px 0px 0px; text-wrap: pretty;"><span class="sc-interp">The Great Migration</span></h3>
                  <p data-dc-tpl="47" style="font-size: 15px; line-height: 1.65; color: rgb(107, 101, 88); margin: 10px 0px 0px;"><span class="sc-interp">River crossings by morning, open plains by dusk, from camps that move with the herds.</span></p>
                  <div data-dc-tpl="48" style="display: flex; align-items: center; gap: 12px; margin-top: 16px; padding-top: 14px; border-top: 1px solid rgb(222, 214, 198); font-size: 13px; color: rgb(28, 26, 23);">
                    <span data-dc-tpl="49"><span class="sc-interp">7 nights</span></span>
                    <span data-dc-tpl="50" style="color: rgb(201, 191, 169);">/</span>
                    <span data-dc-tpl="51" style="color: rgb(107, 101, 88);"><span class="sc-interp">from $6,500 pp</span></span>
                  </div>
                </div>
              </a>
            
          </div>
        
        
      </div>
    </section>

    <section data-dc-tpl="58" id="destinations" style="padding: 0px clamp(20px, 6vw, 88px) clamp(72px, 9vw, 120px);">
      <div data-dc-tpl="59" style="max-width: 1200px; margin: 0px auto;">
        <div data-dc-tpl="60" style="font-size: 12px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63);">Where we work</div>
        <h2 data-dc-tpl="61" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 300; font-size: clamp(30px, 3.6vw, 42px); line-height: 1.15; margin: 14px 0px clamp(32px, 4vw, 52px); max-width: 20ch; text-wrap: pretty;">The coast and the highlands</h2>
        <div data-dc-tpl="62" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: clamp(20px, 2.6vw, 32px);">
          
            <div data-dc-tpl="64" class="sc-card" style="position: relative; height: clamp(360px, 42vw, 520px); overflow: hidden; border-radius: 16px;">
              <div data-dc-tpl="65" style="position: absolute; inset: 0px;">
                <img src="/malindi/moorings.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
              </div>
              <div data-dc-tpl="67" style="position: absolute; inset: 0px; background: linear-gradient(0deg, rgba(16, 14, 11, 0.66) 0%, rgba(16, 14, 11, 0.12) 52%, rgba(16, 14, 11, 0) 100%); pointer-events: none;"></div>
              <div data-dc-tpl="68" style="position: absolute; left: 0px; right: 0px; bottom: 0px; padding: clamp(24px, 3vw, 36px); pointer-events: none;">
                <div data-dc-tpl="69" style="font-size: 11px; font-weight: 500; letter-spacing: 0.16em; text-transform: uppercase; color: rgb(228, 199, 154);"><span class="sc-interp">Diani · Watamu</span></div>
                <h3 data-dc-tpl="70" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 300; font-size: clamp(28px, 3.2vw, 38px); line-height: 1.15; color: rgb(253, 251, 246); margin: 10px 0px 0px;"><span class="sc-interp">The coast</span></h3>
                <p data-dc-tpl="71" style="font-size: 16px; line-height: 1.6; color: rgb(241, 234, 220); max-width: 38ch; margin: 10px 0px 0px;"><span class="sc-interp">Warm water year round, a living reef, and hotels small enough to know your name.</span></p>
              </div>
            </div>
          
            <div data-dc-tpl="64" class="sc-card" style="position: relative; height: clamp(360px, 42vw, 520px); overflow: hidden; border-radius: 16px;">
              <div data-dc-tpl="65" style="position: absolute; inset: 0px;">
                <img src="/malindi/mangroves.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
              </div>
              <div data-dc-tpl="67" style="position: absolute; inset: 0px; background: linear-gradient(0deg, rgba(16, 14, 11, 0.66) 0%, rgba(16, 14, 11, 0.12) 52%, rgba(16, 14, 11, 0) 100%); pointer-events: none;"></div>
              <div data-dc-tpl="68" style="position: absolute; left: 0px; right: 0px; bottom: 0px; padding: clamp(24px, 3vw, 36px); pointer-events: none;">
                <div data-dc-tpl="69" style="font-size: 11px; font-weight: 500; letter-spacing: 0.16em; text-transform: uppercase; color: rgb(228, 199, 154);"><span class="sc-interp">Nanyuki · Mount Kenya</span></div>
                <h3 data-dc-tpl="70" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 300; font-size: clamp(28px, 3.2vw, 38px); line-height: 1.15; color: rgb(253, 251, 246); margin: 10px 0px 0px;"><span class="sc-interp">The highlands</span></h3>
                <p data-dc-tpl="71" style="font-size: 16px; line-height: 1.6; color: rgb(241, 234, 220); max-width: 38ch; margin: 10px 0px 0px;"><span class="sc-interp">Cold mornings, high plains, and wildlife on private conservancy land.</span></p>
              </div>
            </div>
          
        </div>
      </div>
    </section>

    <section data-dc-tpl="72" id="how-it-works" style="padding: clamp(72px, 9vw, 120px) clamp(20px, 6vw, 88px); border-top: 1px solid rgb(222, 214, 198);">
      <div data-dc-tpl="73" style="max-width: 1200px; margin: 0px auto;">
        <div data-dc-tpl="74" style="font-size: 12px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63);">How a custom trip works</div>
        <h2 data-dc-tpl="75" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 300; font-size: clamp(30px, 3.6vw, 42px); line-height: 1.15; margin: 14px 0px clamp(40px, 5vw, 64px); max-width: 22ch; text-wrap: pretty;">Four steps, no pressure at any of them</h2>
        <div data-dc-tpl="76" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: clamp(24px, 3vw, 44px);">
          
            <div data-dc-tpl="78" style="border-top: 1px solid rgb(28, 26, 23); padding-top: 20px;">
              <div data-dc-tpl="79" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-size: 30px; font-weight: 400; color: rgb(150, 112, 63); line-height: 1;"><span class="sc-interp">01</span></div>
              <h3 data-dc-tpl="80" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 22px; line-height: 1.25; margin: 14px 0px 0px;"><span class="sc-interp">Tell us what you dream of</span></h3>
              <p data-dc-tpl="81" style="font-size: 15px; line-height: 1.7; color: rgb(107, 101, 88); margin: 10px 0px 0px;"><span class="sc-interp">A season, a rough number of days, and the kind of trip you want. No form-filling marathon.</span></p>
            </div>
          
            <div data-dc-tpl="78" style="border-top: 1px solid rgb(28, 26, 23); padding-top: 20px;">
              <div data-dc-tpl="79" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-size: 30px; font-weight: 400; color: rgb(150, 112, 63); line-height: 1;"><span class="sc-interp">02</span></div>
              <h3 data-dc-tpl="80" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 22px; line-height: 1.25; margin: 14px 0px 0px;"><span class="sc-interp">We build a real itinerary</span></h3>
              <p data-dc-tpl="81" style="font-size: 15px; line-height: 1.7; color: rgb(107, 101, 88); margin: 10px 0px 0px;"><span class="sc-interp">Named properties, a workable route, and a price — not a brochure.</span></p>
            </div>
          
            <div data-dc-tpl="78" style="border-top: 1px solid rgb(28, 26, 23); padding-top: 20px;">
              <div data-dc-tpl="79" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-size: 30px; font-weight: 400; color: rgb(150, 112, 63); line-height: 1;"><span class="sc-interp">03</span></div>
              <h3 data-dc-tpl="80" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 22px; line-height: 1.25; margin: 14px 0px 0px;"><span class="sc-interp">We refine it together</span></h3>
              <p data-dc-tpl="81" style="font-size: 15px; line-height: 1.7; color: rgb(107, 101, 88); margin: 10px 0px 0px;"><span class="sc-interp">Swap a lodge, add nights, change the order. As many passes as you need.</span></p>
            </div>
          
            <div data-dc-tpl="78" style="border-top: 1px solid rgb(28, 26, 23); padding-top: 20px;">
              <div data-dc-tpl="79" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-size: 30px; font-weight: 400; color: rgb(150, 112, 63); line-height: 1;"><span class="sc-interp">04</span></div>
              <h3 data-dc-tpl="80" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 22px; line-height: 1.25; margin: 14px 0px 0px;"><span class="sc-interp">You travel</span></h3>
              <p data-dc-tpl="81" style="font-size: 15px; line-height: 1.7; color: rgb(107, 101, 88); margin: 10px 0px 0px;"><span class="sc-interp">One number to call while you are here, answered by someone in Kenya.</span></p>
            </div>
          
        </div>
      </div>
    </section>

    <section data-dc-tpl="82" style="padding: 0px clamp(20px, 6vw, 88px) clamp(72px, 9vw, 120px);">
      <div data-dc-tpl="83" style="max-width: 1200px; margin: 0px auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: clamp(32px, 5vw, 72px); align-items: start;">
        <div data-dc-tpl="84">
          <div data-dc-tpl="85" style="font-size: 12px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(150, 112, 63);">Why Heissal</div>
          <h2 data-dc-tpl="86" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 300; font-size: clamp(30px, 3.6vw, 42px); line-height: 1.15; margin: 14px 0px 0px; max-width: 18ch; text-wrap: pretty;">We only sell what we have slept in</h2>
          <p data-dc-tpl="87" style="font-size: 17px; line-height: 1.7; color: rgb(107, 101, 88); max-width: 44ch; margin: 22px 0px 0px;">Heissal is a small Kenyan operation. The properties on this site are ones we have stayed at, the guides are people we know by name, and the price you are quoted is the price you pay.</p>
        </div>
        <div data-dc-tpl="88" style="display: flex; flex-direction: column; gap: 28px;">
          
            <div data-dc-tpl="90" style="border-top: 1px solid rgb(222, 214, 198); padding-top: 18px;">
              <h3 data-dc-tpl="91" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 22px; line-height: 1.25; margin: 0px;"><span class="sc-interp">Hand-picked properties</span></h3>
              <p data-dc-tpl="92" style="font-size: 15px; line-height: 1.7; color: rgb(107, 101, 88); margin: 8px 0px 0px; max-width: 52ch;"><span class="sc-interp">Nothing appears on this site that we have not visited and stayed in ourselves.</span></p>
            </div>
          
            <div data-dc-tpl="90" style="border-top: 1px solid rgb(222, 214, 198); padding-top: 18px;">
              <h3 data-dc-tpl="91" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 22px; line-height: 1.25; margin: 0px;"><span class="sc-interp">Transparent pricing</span></h3>
              <p data-dc-tpl="92" style="font-size: 15px; line-height: 1.7; color: rgb(107, 101, 88); margin: 8px 0px 0px; max-width: 52ch;"><span class="sc-interp">You see what the trip costs before you speak to anyone, and the quote holds.</span></p>
            </div>
          
            <div data-dc-tpl="90" style="border-top: 1px solid rgb(222, 214, 198); padding-top: 18px;">
              <h3 data-dc-tpl="91" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 400; font-size: 22px; line-height: 1.25; margin: 0px;"><span class="sc-interp">Local expertise</span></h3>
              <p data-dc-tpl="92" style="font-size: 15px; line-height: 1.7; color: rgb(107, 101, 88); margin: 8px 0px 0px; max-width: 52ch;"><span class="sc-interp">Kenyan-run, coast and highlands, with guides we have worked with for years.</span></p>
            </div>
          
        </div>
      </div>
    </section>

    <section data-dc-tpl="93" style="padding: 0px clamp(20px, 6vw, 88px) clamp(72px, 9vw, 120px);">
      <div data-dc-tpl="94" style="max-width: 1200px; margin: 0px auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: clamp(12px, 1.6vw, 20px);">
        
          <div data-dc-tpl="96" style="height: clamp(220px, 24vw, 300px); overflow: hidden; border-radius: 12px;">
            <img src="/malindi/kitesurf.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
          </div>
        
          <div data-dc-tpl="96" style="height: clamp(220px, 24vw, 300px); overflow: hidden; border-radius: 12px;">
            <img src="/malindi/sunset.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
          </div>
        
          <div data-dc-tpl="96" style="height: clamp(220px, 24vw, 300px); overflow: hidden; border-radius: 12px;">
            <img src="/malindi/ocean-safari.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
          </div>
        
          <div data-dc-tpl="96" style="height: clamp(220px, 24vw, 300px); overflow: hidden; border-radius: 12px;">
            <img src="/malindi/shallows.jpg" alt="" style="width:100%;height:100%;object-fit:cover;display:block">
          </div>
        
      </div>
    </section>

    <section data-dc-tpl="98" style="background: rgb(30, 71, 65); padding: clamp(72px, 9vw, 120px) clamp(20px, 6vw, 88px);">
      <div data-dc-tpl="99" style="max-width: 1200px; margin: 0px auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: clamp(32px, 5vw, 64px); align-items: center;">
        <div data-dc-tpl="100">
          <div data-dc-tpl="101" style="font-size: 12px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: rgb(228, 199, 154);">Enquire</div>
          <h2 data-dc-tpl="102" style="font-family: &quot;Cormorant Garamond&quot;, Georgia, serif; font-weight: 300; font-size: clamp(30px, 3.8vw, 46px); line-height: 1.14; color: rgb(253, 251, 246); margin: 16px 0px 0px; max-width: 20ch; text-wrap: pretty;">Tell us what you have in mind</h2>
          <p data-dc-tpl="103" style="font-size: 17px; line-height: 1.7; color: rgb(220, 231, 226); max-width: 44ch; margin: 18px 0px 0px;">One reply, from a person, with an itinerary you can react to. No call centre and no obligation.</p>
        </div>
        <div data-dc-tpl="104" style="display: flex; flex-direction: column; gap: 18px; align-items: flex-start;">
          <a href="/enquire" data-dc-tpl="105" class="scp2" style="cursor: pointer; background: rgb(247, 243, 236); color: rgb(28, 26, 23); padding: 18px 36px; font-size: 12px; font-weight: 500; letter-spacing: 0.13em; text-transform: uppercase; border-radius: 8px;" style="text-decoration:none">Request a custom trip</a>
          <div data-dc-tpl="106" style="font-size: 15px; color: rgb(220, 231, 226); line-height: 1.7;">Or WhatsApp us on <span class="sc-interp">+254 700 000 000</span><br data-dc-tpl="107"><span class="sc-interp">hello@heissal.tours</span></div>
        </div>
      </div>
    </section>

  `;

export default async function Home() {
  // The design import carries a placeholder WhatsApp number and email
  // wherever it mentions contacting us; swapped here for the real ones from
  // the same DocumentConfig the quotation document prints (see
  // lib/api.ts:contact), rather than leaving a fabricated phone number live
  // on the page most visitors actually land on.
  const info = await contact();
  const html = HTML.replace(/\+254 700 000 000/g, info.contact_phone || "+254 700 000 000").replace(
    /hello@heissal\.tours/g,
    info.contact_email || "hello@heissal.tours",
  );
  return (
    <>
      <Hero />
      <div dangerouslySetInnerHTML={{ __html: html }} />
    </>
  );
}
