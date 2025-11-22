/**
 * @krisspy-file
 * @type page
 * @name "RetroRainbowDesignSystem"
 * @title "Retro Rainbow Design System"
 * @description "Comprehensive design system showcase featuring retro rainbow palette, glass effects, and accessible components"
 * @routes ["/design"]
 * @design "reference"
 */

import { Heart, Play, Pause, Volume2, Radio, Music, Zap, Eye, Sparkles, Palette } from 'lucide-react';
import { useState } from 'react';

export default function RetroRainbowDesignSystem() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeSection, setActiveSection] = useState<string>('colors');

  const tabs = [
    { id: 'colors', label: 'Retro Rainbow Palette' },
    { id: 'typography', label: 'Typography' },
    { id: 'buttons', label: 'Buttons' },
    { id: 'cards', label: 'Glass Cards' },
    { id: 'forms', label: 'Forms' },
    { id: 'components', label: 'Components' },
  ];

  const retroColors = [
    { name: 'Teal Dark', class: 'bg-teal', hex: '#025c7f' },
    { name: 'Teal Light', class: 'bg-teal-light', hex: '#027b96' },
    { name: 'Cyan', class: 'bg-cyan', hex: '#069aa4' },
    { name: 'Mint', class: 'bg-mint', hex: '#87d1ac' },
    { name: 'Cream', class: 'bg-cream', hex: '#fef8be' },
    { name: 'Peach Light', class: 'bg-peach', hex: '#ffc991' },
    { name: 'Coral', class: 'bg-coral', hex: '#fb9481' },
    { name: 'Salmon/Pink', class: 'bg-salmon', hex: '#f37986' },
  ];

  return (
    <div className="min-h-screen bg-primary text-primary">
      {/* Hero Header with Glass Effect */}
      <header className="sticky top-0 z-40 glass border-b border-primary">
        <div className="max-w-7xl mx-auto px-lg py-2xl flex items-center justify-between">
          <div className="flex items-center gap-md">
            <div className="w-12 h-12 bg-gradient-to-br from-cyan via-mint to-peach rounded-lg flex items-center justify-center shadow-lg">
              <Palette className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="header-retro header-retro-lg text-primary">Retro Rainbow</h1>
              <p className="text-secondary text-sm font-semibold">Design System v1.0</p>
            </div>
          </div>
          <div className="hidden md:flex gap-md">
            <button className="btn btn-secondary">Documentation</button>
            <button className="btn btn-primary">Get Started</button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs with Glass */}
      <nav className="bg-secondary/5 glass border-b border-primary sticky top-[80px] z-30 overflow-x-auto">
        <div className="max-w-7xl mx-auto px-lg flex gap-lg">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSection(tab.id)}
              className={`py-lg px-md border-b-4 transition-all duration-300 whitespace-nowrap font-600 ${
                activeSection === tab.id
                  ? 'border-cyan text-cyan'
                  : 'border-transparent text-secondary hover:text-primary'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-lg py-2xl">
        {/* Colors Section */}
        {activeSection === 'colors' && (
          <section className="space-y-2xl animate-fade-in">
            <div>
              <h2 className="header-retro header-retro-lg text-primary mb-md">Retro Rainbow Palette</h2>
              <p className="text-secondary mb-2xl">A vibrant 8-color retro inspired palette with accessible contrast</p>
            </div>

            {/* Main Palette Grid */}
            <div>
              <h3 className="text-xl font-bold mb-lg text-primary">Full Spectrum</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-md">
                {retroColors.map((color) => (
                  <div key={color.name} className="group cursor-pointer">
                    <div
                      className={`${color.class} h-24 rounded-lg shadow-lg transition-transform hover:scale-105 mb-md`}
                    />
                    <div className="text-center">
                      <p className="font-bold text-primary text-sm">{color.name}</p>
                      <p className="text-secondary text-xs font-mono">{color.hex}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Color Groupings */}
            <div className="grid md:grid-cols-2 gap-2xl">
              {/* Cool Tones */}
              <div className="card">
                <h3 className="text-lg font-bold mb-lg text-primary flex items-center gap-md">
                  <div className="w-4 h-4 bg-cyan rounded" />
                  Cool Tones (Primary)
                </h3>
                <div className="space-y-md">
                  <div className="flex items-center gap-md">
                    <div className="w-12 h-12 bg-teal rounded-md" />
                    <div>
                      <p className="font-bold text-primary">Teal Dark</p>
                      <p className="text-secondary text-sm">#025c7f - Primary Action</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-md">
                    <div className="w-12 h-12 bg-cyan rounded-md" />
                    <div>
                      <p className="font-bold text-primary">Cyan</p>
                      <p className="text-secondary text-sm">#069aa4 - Secondary Action</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-md">
                    <div className="w-12 h-12 bg-mint rounded-md" />
                    <div>
                      <p className="font-bold text-primary">Mint</p>
                      <p className="text-secondary text-sm">#87d1ac - Success State</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Warm Tones */}
              <div className="card">
                <h3 className="text-lg font-bold mb-lg text-primary flex items-center gap-md">
                  <div className="w-4 h-4 bg-peach rounded" />
                  Warm Tones (Accents)
                </h3>
                <div className="space-y-md">
                  <div className="flex items-center gap-md">
                    <div className="w-12 h-12 bg-peach rounded-md" />
                    <div>
                      <p className="font-bold text-primary">Peach</p>
                      <p className="text-secondary text-sm">#ffc991 - Warning State</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-md">
                    <div className="w-12 h-12 bg-coral rounded-md" />
                    <div>
                      <p className="font-bold text-primary">Coral</p>
                      <p className="text-secondary text-sm">#fb9481 - Accent</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-md">
                    <div className="w-12 h-12 bg-salmon rounded-md" />
                    <div>
                      <p className="font-bold text-primary">Salmon/Pink</p>
                      <p className="text-secondary text-sm">#f37986 - Danger State</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Typography Section */}
        {activeSection === 'typography' && (
          <section className="space-y-2xl animate-fade-in">
            <div>
              <h2 className="header-retro header-retro-lg text-primary mb-md">Typography</h2>
              <p className="text-secondary mb-2xl">
                Fredoka One for headers (thick retro look). Nunito for body text. Maximum visual impact! 🎨
              </p>
            </div>

            {/* Heading Scale */}
            <div className="card">
              <h3 className="header-retro header-retro-md text-primary mb-lg">Heading Scale</h3>
              <div className="space-y-2xl">
                <div>
                  <p className="text-secondary text-sm mb-md">H1 - Display (3.5rem, Fredoka One, Weight 900)</p>
                  <h1 className="text-primary">The Quick Brown Fox</h1>
                </div>
                <div>
                  <p className="text-secondary text-sm mb-md">H2 - Large Heading (2.5rem, Fredoka One, Weight 900)</p>
                  <h2 className="text-primary">The Quick Brown Fox</h2>
                </div>
                <div>
                  <p className="text-secondary text-sm mb-md">H3 - Medium Heading (1.75rem, Fredoka One, Weight 800)</p>
                  <h3 className="text-primary">The Quick Brown Fox</h3>
                </div>
              </div>
            </div>

            {/* Body Text Scale */}
            <div className="card">
              <h3 className="text-xl font-bold mb-lg text-primary">Body Text Scale</h3>
              <div className="space-y-lg">
                <div>
                  <p className="text-secondary text-xs mb-md">16px - Body Large (Font Weight 500)</p>
                  <p className="text-base text-primary">
                    The quick brown fox jumps over the lazy dog. This is example body text in Nunito.
                  </p>
                </div>
                <div>
                  <p className="text-secondary text-xs mb-md">14px - Body (Font Weight 400)</p>
                  <p className="text-sm text-primary">
                    The quick brown fox jumps over the lazy dog. This is example body text in Nunito.
                  </p>
                </div>
                <div>
                  <p className="text-secondary text-xs mb-md">12px - Small (Font Weight 400)</p>
                  <p className="text-xs text-secondary">
                    The quick brown fox jumps over the lazy dog. This is example small text in Nunito.
                  </p>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Buttons Section */}
        {activeSection === 'buttons' && (
          <section className="space-y-2xl animate-fade-in">
            <div>
              <h2 className="header-retro header-retro-lg text-primary mb-md">Button Styles</h2>
              <p className="text-secondary mb-2xl">Touch-friendly buttons with gradient fills and glass variants</p>
            </div>

            {/* Primary Buttons */}
            <div className="card">
              <h3 className="text-lg font-bold mb-lg text-primary">Primary Buttons</h3>
              <div className="flex flex-wrap gap-lg items-center">
                <button className="btn btn-primary">
                  <Play className="w-4 h-4" />
                  Get Started
                </button>
                <button className="btn btn-primary">Primary Action</button>
                <button className="btn btn-primary" disabled>
                  Disabled
                </button>
              </div>
            </div>

            {/* Secondary Buttons */}
            <div className="card">
              <h3 className="text-lg font-bold mb-lg text-primary">Secondary Buttons</h3>
              <div className="flex flex-wrap gap-lg items-center">
                <button className="btn btn-secondary">
                  <Pause className="w-4 h-4" />
                  Secondary
                </button>
                <button className="btn btn-secondary">Learn More</button>
                <button className="btn btn-secondary" disabled>
                  Disabled
                </button>
              </div>
            </div>

            {/* Ghost Buttons */}
            <div className="card">
              <h3 className="text-lg font-bold mb-lg text-primary">Ghost Buttons</h3>
              <div className="flex flex-wrap gap-lg items-center">
                <button className="btn btn-ghost">
                  <Volume2 className="w-4 h-4" />
                  Ghost Style
                </button>
                <button className="btn btn-ghost">Optional Action</button>
                <button className="btn btn-ghost" disabled>
                  Disabled
                </button>
              </div>
            </div>

            {/* Glass Buttons */}
            <div className="card-glass">
              <h3 className="text-lg font-bold mb-lg text-primary">Glass Buttons</h3>
              <div className="flex flex-wrap gap-lg items-center">
                <button className="btn btn-glass">
                  <Sparkles className="w-4 h-4" />
                  Glass Effect
                </button>
                <button className="btn btn-glass">Frosted Look</button>
              </div>
            </div>

            {/* Icon Buttons */}
            <div className="card">
              <h3 className="text-lg font-bold mb-lg text-primary">Icon Buttons</h3>
              <div className="flex flex-wrap gap-lg items-center">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="w-14 h-14 rounded-full bg-gradient-to-br from-cyan to-mint text-white flex items-center justify-center transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-110"
                >
                  {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
                </button>
                <button className="w-14 h-14 rounded-full bg-peach text-white flex items-center justify-center transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-110">
                  <Heart className="w-6 h-6" />
                </button>
                <button className="w-14 h-14 rounded-full bg-salmon text-white flex items-center justify-center transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-110">
                  <Radio className="w-6 h-6" />
                </button>
              </div>
            </div>
          </section>
        )}

        {/* Glass Cards Section */}
        {activeSection === 'cards' && (
          <section className="space-y-2xl animate-fade-in">
            <div>
              <h2 className="header-retro header-retro-lg text-primary mb-md">Glass Cards & Components</h2>
              <p className="text-secondary mb-2xl">Modern glass morphism effects with backdrop blur</p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-lg">
              {/* Standard Card */}
              <div className="card">
                <div className="w-full h-32 bg-gradient-to-br from-mint to-cyan rounded-lg mb-lg flex items-center justify-center">
                  <Music className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-lg font-bold mb-sm text-primary">Standard Card</h3>
                <p className="text-secondary text-sm mb-lg">Clean, accessible card with subtle shadow</p>
                <button className="btn btn-primary w-full">Explore</button>
              </div>

              {/* Interactive Card */}
              <div className="card-interactive group">
                <div className="w-full h-32 bg-gradient-to-br from-peach to-coral rounded-lg mb-lg flex items-center justify-center group-hover:from-salmon group-hover:to-peach transition-all">
                  <Play className="w-8 h-8 text-white group-hover:scale-110 transition-transform" />
                </div>
                <h3 className="text-lg font-bold mb-sm text-primary">Interactive Card</h3>
                <p className="text-secondary text-sm">Hover for smooth transitions and effects</p>
              </div>

              {/* Glass Card */}
              <div className="card-glass">
                <Sparkles className="w-6 h-6 text-cyan mb-lg" />
                <h3 className="text-lg font-bold mb-sm text-primary">Glass Card</h3>
                <p className="text-secondary text-sm mb-lg">Modern frosted glass effect with backdrop blur</p>
                <div className="w-full h-2 bg-white/20 rounded-full overflow-hidden">
                  <div className="h-full w-2/3 bg-gradient-to-r from-cyan to-mint rounded-full" />
                </div>
              </div>
            </div>

            {/* Featured Card with Gradient */}
            <div className="bg-gradient-to-br from-cyan/20 via-mint/10 to-peach/20 rounded-lg p-2xl border border-cyan/30 shadow-lg">
              <div className="flex items-start gap-lg">
                <Zap className="w-8 h-8 text-cyan flex-shrink-0 mt-1" />
                <div>
                  <h3 className="text-lg font-bold mb-sm text-primary">Featured Highlight</h3>
                  <p className="text-secondary">
                    A gradient card with subtle retro rainbow colors creating visual hierarchy
                  </p>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Forms Section */}
        {activeSection === 'forms' && (
          <section className="space-y-2xl animate-fade-in">
            <div>
              <h2 className="header-retro header-retro-lg text-primary mb-md">Form Elements</h2>
              <p className="text-secondary mb-2xl">Accessible form inputs with retro styling and glass variants</p>
            </div>

            <div className="grid md:grid-cols-2 gap-2xl">
              {/* Standard Form */}
              <div className="card">
                <h3 className="text-lg font-bold mb-lg text-primary">Standard Inputs</h3>
                <div className="space-y-lg">
                  <div>
                    <label className="block text-sm font-bold mb-md text-primary">Full Name</label>
                    <input
                      type="text"
                      placeholder="Enter your full name"
                      className="input"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-bold mb-md text-primary">Email Address</label>
                    <input
                      type="email"
                      placeholder="your.email@example.com"
                      className="input"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-bold mb-md text-primary">Message</label>
                    <textarea
                      placeholder="Share your thoughts..."
                      className="input resize-none"
                      rows={4}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-bold mb-md text-primary">Category</label>
                    <select className="input">
                      <option>Select a category</option>
                      <option>Feature Request</option>
                      <option>Bug Report</option>
                      <option>General Feedback</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Glass Form */}
              <div className="card-glass">
                <h3 className="text-lg font-bold mb-lg text-primary">Glass Inputs</h3>
                <div className="space-y-lg">
                  <div>
                    <label className="block text-sm font-bold mb-md text-primary">Username</label>
                    <input
                      type="text"
                      placeholder="Choose your username"
                      className="input-glass"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-bold mb-md text-primary">Password</label>
                    <input
                      type="password"
                      placeholder="••••••••"
                      className="input-glass"
                    />
                  </div>

                  <div className="space-y-md">
                    <label className="flex items-center gap-md cursor-pointer">
                      <input
                        type="checkbox"
                        className="w-5 h-5 rounded border-2 border-primary accent-cyan cursor-pointer"
                      />
                      <span className="text-sm font-medium text-primary">Remember me</span>
                    </label>

                    <label className="flex items-center gap-md cursor-pointer">
                      <input
                        type="radio"
                        name="contact"
                        className="w-5 h-5 border-2 border-primary accent-cyan cursor-pointer"
                      />
                      <span className="text-sm font-medium text-primary">Contact via email</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Components Section */}
        {activeSection === 'components' && (
          <section className="space-y-2xl animate-fade-in">
            <div>
              <h2 className="header-retro header-retro-lg text-primary mb-md">Additional Components</h2>
              <p className="text-secondary mb-2xl">Badges, progress bars, alerts, and spacing systems</p>
            </div>

            {/* Badges */}
            <div className="card">
              <h3 className="text-lg font-bold mb-lg text-primary">Status Badges</h3>
              <div className="flex flex-wrap gap-md">
                <span className="px-lg py-md bg-mint/20 text-mint rounded-full text-sm font-bold border border-mint/40">
                  ✓ Success
                </span>
                <span className="px-lg py-md bg-cyan/20 text-cyan rounded-full text-sm font-bold border border-cyan/40">
                  ℹ Information
                </span>
                <span className="px-lg py-md bg-peach/20 text-peach rounded-full text-sm font-bold border border-peach/40">
                  ⚠ Warning
                </span>
                <span className="px-lg py-md bg-salmon/20 text-salmon rounded-full text-sm font-bold border border-salmon/40">
                  ✕ Error
                </span>
              </div>
            </div>

            {/* Progress Bars */}
            <div className="card">
              <h3 className="text-lg font-bold mb-lg text-primary">Progress Indicators</h3>
              <div className="space-y-lg max-w-md">
                <div>
                  <div className="flex justify-between text-sm mb-md">
                    <span className="font-bold text-primary">Loading</span>
                    <span className="text-secondary">65%</span>
                  </div>
                  <div className="w-full h-2 bg-tertiary rounded-full overflow-hidden">
                    <div className="h-full w-[65%] bg-gradient-to-r from-cyan to-mint rounded-full transition-all duration-500" />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-md">
                    <span className="font-bold text-primary">Processing</span>
                    <span className="text-secondary">45%</span>
                  </div>
                  <div className="w-full h-2 bg-tertiary rounded-full overflow-hidden">
                    <div className="h-full w-[45%] bg-gradient-to-r from-peach to-coral rounded-full transition-all duration-500" />
                  </div>
                </div>
              </div>
            </div>

            {/* Alert Messages */}
            <div className="card">
              <h3 className="text-lg font-bold mb-lg text-primary">Alert Messages</h3>
              <div className="space-y-md">
                <div className="bg-mint/10 border-l-4 border-mint rounded-md p-lg flex gap-md">
                  <Zap className="w-5 h-5 text-mint flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-bold text-primary">Success</p>
                    <p className="text-sm text-secondary">Your changes have been saved successfully</p>
                  </div>
                </div>

                <div className="bg-cyan/10 border-l-4 border-cyan rounded-md p-lg flex gap-md">
                  <Eye className="w-5 h-5 text-cyan flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-bold text-primary">Information</p>
                    <p className="text-sm text-secondary">Here's some helpful information for you</p>
                  </div>
                </div>

                <div className="bg-peach/10 border-l-4 border-peach rounded-md p-lg flex gap-md">
                  <Zap className="w-5 h-5 text-peach flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-bold text-primary">Warning</p>
                    <p className="text-sm text-secondary">Please review this before proceeding</p>
                  </div>
                </div>

                <div className="bg-salmon/10 border-l-4 border-salmon rounded-md p-lg flex gap-md">
                  <Eye className="w-5 h-5 text-salmon flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-bold text-primary">Error</p>
                    <p className="text-sm text-secondary">Something went wrong, please try again</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Spacing Scale */}
            <div className="card">
              <h3 className="text-lg font-bold mb-lg text-primary">Spacing Scale (4px Base)</h3>
              <div className="space-y-md">
                {['xs', 'sm', 'md', 'lg', 'xl', '2xl'].map((size, idx) => (
                  <div key={size} className="flex items-center gap-4">
                    <span className="text-secondary text-sm font-mono w-12">{size}</span>
                    <span className="text-secondary text-xs">{4 * (idx + 1)}px</span>
                    <div className="h-8 bg-gradient-to-r from-cyan to-mint rounded" style={{ width: `${4 * (idx + 1) * 3}px` }} />
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-primary bg-secondary/5 mt-2xl">
        <div className="max-w-7xl mx-auto px-lg py-2xl">
          <div className="grid md:grid-cols-3 gap-2xl mb-2xl">
            <div>
              <h4 className="font-bold text-primary mb-md">Breakpoints</h4>
              <p className="text-secondary text-sm">Mobile: 0-767px | Tablet: 768-1024px | Desktop: 1025-1440px | Large: 1441px+</p>
            </div>
            <div>
              <h4 className="font-bold text-primary mb-md">Typography</h4>
              <p className="text-secondary text-sm">Headers: Nunito 800 | Body: Nunito 400-700</p>
            </div>
            <div>
              <h4 className="font-bold text-primary mb-md">Spacing</h4>
              <p className="text-secondary text-sm">4px base unit: xs(4px) to 2xl(32px)</p>
            </div>
          </div>
          <div className="border-t border-primary pt-lg text-center text-secondary text-sm">
            <p>© 2025 Retro Rainbow Design System. Touch-friendly, accessible, and retro-inspired. 🌈</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
