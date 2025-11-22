/**
 * @krisspy-file
 * @type page
 * @name "DesignSystemTest"
 * @title "Design System Test"
 * @description "Demo page showcasing the design system with default theme"
 * @routes ["/design-system"]
 * @design "template"
 * @requiresAuth false
 */

import { Heart, Play, Pause, Volume2, Radio, Music, Zap, Eye } from 'lucide-react';
import { useState } from 'react';

export default function DesignSystemTest() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeSection, setActiveSection] = useState<string>('colors');

  const tabs = [
    { id: 'colors', label: 'Colors' },
    { id: 'typography', label: 'Typography' },
    { id: 'buttons', label: 'Buttons' },
    { id: 'cards', label: 'Cards' },
    { id: 'forms', label: 'Forms' },
    { id: 'components', label: 'Components' },
  ];

  return (
    <div className="min-h-screen bg-primary text-primary">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-primary/80 backdrop-blur-md border-b border-primary">
        <div className="max-w-7xl mx-auto px-lg py-lg flex items-center justify-between">
          <div className="flex items-center gap-md">
            <div className="w-10 h-10 bg-blue rounded-md flex items-center justify-center">
              <Music className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-primary">Design System</h1>
          </div>
          <p className="text-secondary text-sm">Theme Showcase</p>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-primary border-b border-primary sticky top-[72px] z-30">
        <div className="max-w-7xl mx-auto px-lg flex gap-lg overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSection(tab.id)}
              className={`py-lg px-md border-b-2 transition-colors duration-200 whitespace-nowrap ${
                activeSection === tab.id
                  ? 'border-blue text-blue'
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
              <h2 className="text-3xl font-bold mb-lg text-primary">Colors</h2>
              <p className="text-secondary mb-2xl">Default color palette</p>
            </div>

            {/* Primary Colors */}
            <div>
              <h3 className="text-xl font-semibold mb-lg text-blue">Primary Colors</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-lg">
                {[
                  { name: 'Primary Blue', bg: 'bg-blue', value: '#3b82f6' },
                  { name: 'Primary Hover', bg: 'bg-blue-hover', value: '#2563eb' },
                  { name: 'Success', bg: 'bg-success', value: '#10b981' },
                  { name: 'Danger', bg: 'bg-danger', value: '#ef4444' },
                ].map((color) => (
                  <div key={color.name} className="space-y-md">
                    <div className={`${color.bg} h-32 rounded-lg shadow-lg`} />
                    <div>
                      <p className="font-semibold text-primary">{color.name}</p>
                      <p className="text-secondary text-sm">{color.value}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Background Colors */}
            <div>
              <h3 className="text-xl font-semibold mb-lg text-primary">Background Colors</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-lg">
                {[
                  { name: 'Primary', bg: 'bg-primary', value: '#FFFFFF' },
                  { name: 'Secondary', bg: 'bg-secondary', value: '#F7F7F7' },
                  { name: 'Tertiary', bg: 'bg-tertiary', value: '#E0E0E0' },
                ].map((color) => (
                  <div key={color.name} className="space-y-md">
                    <div className={`${color.bg} h-32 rounded-lg shadow-lg border border-primary`} />
                    <div>
                      <p className="font-semibold text-primary">{color.name}</p>
                      <p className="text-secondary text-sm">{color.value}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Text Colors */}
            <div>
              <h3 className="text-xl font-semibold mb-lg text-primary">Text Colors</h3>
              <div className="space-y-md">
                <div className="text-primary text-2xl">Primary Text Color</div>
                <div className="text-secondary text-2xl">Secondary Text Color</div>
                <div className="text-blue text-2xl">Blue Text Color</div>
                <div className="text-success text-2xl">Success Text Color</div>
                <div className="text-danger text-2xl">Danger Text Color</div>
              </div>
            </div>
          </section>
        )}

        {/* Typography Section */}
        {activeSection === 'typography' && (
          <section className="space-y-2xl animate-fade-in">
            <div>
              <h2 className="text-3xl font-bold mb-lg text-primary">Typography</h2>
              <p className="text-secondary mb-2xl">Font sizes and text styles</p>
            </div>

            <div className="space-y-lg">
              {[
                { label: '4XL - Display', className: 'text-4xl font-bold' },
                { label: '3XL - Heading', className: 'text-3xl font-bold' },
                { label: '2XL - Large Heading', className: 'text-2xl font-semibold' },
                { label: 'XL - Medium Heading', className: 'text-xl font-semibold' },
                { label: 'LG - Large Text', className: 'text-lg font-medium' },
                { label: 'BASE - Body Text', className: 'text-base font-normal' },
                { label: 'SM - Small Text', className: 'text-sm font-normal' },
                { label: 'XS - Extra Small', className: 'text-xs font-normal' },
              ].map((text) => (
                <div key={text.label} className={`${text.className} text-primary`}>
                  {text.label}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Buttons Section */}
        {activeSection === 'buttons' && (
          <section className="space-y-2xl animate-fade-in">
            <div>
              <h2 className="text-3xl font-bold mb-lg text-primary">Buttons</h2>
              <p className="text-secondary mb-2xl">Button styles and states</p>
            </div>

            {/* Primary Buttons */}
            <div>
              <h3 className="text-xl font-semibold mb-lg text-primary">Primary Buttons</h3>
              <div className="flex flex-wrap gap-lg">
                <button className="btn btn-primary">
                  <Play className="w-4 h-4" />
                  Play
                </button>
                <button className="btn btn-primary">
                  Action Button
                </button>
                <button className="btn btn-primary" disabled>
                  Disabled
                </button>
              </div>
            </div>

            {/* Secondary Buttons */}
            <div>
              <h3 className="text-xl font-semibold mb-lg text-primary">Secondary Buttons</h3>
              <div className="flex flex-wrap gap-lg">
                <button className="btn btn-secondary">
                  <Pause className="w-4 h-4" />
                  Pause
                </button>
                <button className="btn btn-secondary">Like</button>
                <button className="btn btn-secondary" disabled>
                  Disabled
                </button>
              </div>
            </div>

            {/* Ghost Buttons */}
            <div>
              <h3 className="text-xl font-semibold mb-lg text-primary">Ghost Buttons</h3>
              <div className="flex flex-wrap gap-lg">
                <button className="btn btn-ghost">
                  <Volume2 className="w-4 h-4" />
                  Volume
                </button>
                <button className="btn btn-ghost">More Options</button>
                <button className="btn btn-ghost" disabled>
                  Disabled
                </button>
              </div>
            </div>

            {/* Icon Buttons */}
            <div>
              <h3 className="text-xl font-semibold mb-lg text-primary">Icon Buttons</h3>
              <div className="flex flex-wrap gap-lg">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="w-12 h-12 rounded-full bg-blue hover:bg-blue-hover text-white flex items-center justify-center transition-all duration-200 shadow"
                >
                  {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
                </button>
                <button className="w-12 h-12 rounded-full bg-secondary hover:bg-tertiary text-blue flex items-center justify-center transition-all duration-200 border border-primary">
                  <Heart className="w-6 h-6" />
                </button>
                <button className="w-12 h-12 rounded-full bg-secondary hover:bg-tertiary text-primary flex items-center justify-center transition-all duration-200 border border-primary">
                  <Radio className="w-6 h-6" />
                </button>
              </div>
            </div>
          </section>
        )}

        {/* Cards Section */}
        {activeSection === 'cards' && (
          <section className="space-y-2xl animate-fade-in">
            <div>
              <h2 className="text-3xl font-bold mb-lg text-primary">Cards</h2>
              <p className="text-secondary mb-2xl">Card components and layouts</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
              {/* Basic Card */}
              <div className="card">
                <div className="w-full h-32 bg-tertiary rounded-md mb-lg flex items-center justify-center">
                  <Music className="w-8 h-8 text-secondary" />
                </div>
                <h3 className="text-lg font-semibold mb-sm text-primary">Card Title</h3>
                <p className="text-secondary text-sm mb-lg">
                  A basic card component with content
                </p>
                <button className="btn btn-primary w-full">Action</button>
              </div>

              {/* Interactive Card */}
              <div className="card-interactive group">
                <div className="w-full h-32 bg-tertiary rounded-md mb-lg flex items-center justify-center group-hover:bg-blue/20 transition-colors">
                  <Play className="w-8 h-8 text-secondary group-hover:text-blue transition-colors" />
                </div>
                <h3 className="text-lg font-semibold mb-sm text-primary">Interactive Card</h3>
                <p className="text-secondary text-sm">
                  Hover over me for interactive effects
                </p>
              </div>

              {/* Featured Card */}
              <div className="bg-gradient-to-br from-blue/20 to-blue/5 rounded-lg p-lg border border-blue/30 shadow-lg">
                <Zap className="w-8 h-8 text-blue mb-lg" />
                <h3 className="text-lg font-semibold mb-sm text-primary">Featured</h3>
                <p className="text-secondary text-sm">
                  A featured card with gradient and shadow effect
                </p>
              </div>
            </div>
          </section>
        )}

        {/* Forms Section */}
        {activeSection === 'forms' && (
          <section className="space-y-2xl animate-fade-in">
            <div>
              <h2 className="text-3xl font-bold mb-lg text-primary">Forms</h2>
              <p className="text-secondary mb-2xl">Form inputs and elements</p>
            </div>

            <div className="max-w-md space-y-lg">
              <div>
                <label className="block text-sm font-medium mb-md text-primary">Text Input</label>
                <input
                  type="text"
                  placeholder="Enter your text..."
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-md text-primary">Search</label>
                <input
                  type="text"
                  placeholder="Search..."
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-md text-primary">Textarea</label>
                <textarea
                  placeholder="Enter your message..."
                  className="input resize-none"
                  rows={4}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-md text-primary">Select</label>
                <select className="input">
                  <option>Choose an option</option>
                  <option>Option 1</option>
                  <option>Option 2</option>
                </select>
              </div>

              <div>
                <label className="flex items-center gap-md cursor-pointer">
                  <input
                    type="checkbox"
                    className="w-4 h-4 rounded border-primary accent-blue cursor-pointer"
                  />
                  <span className="text-sm text-primary">Save my preferences</span>
                </label>
              </div>

              <div>
                <label className="flex items-center gap-md cursor-pointer">
                  <input
                    type="radio"
                    name="option"
                    className="w-4 h-4 border-primary accent-blue cursor-pointer"
                  />
                  <span className="text-sm text-primary">Option A</span>
                </label>
              </div>
            </div>
          </section>
        )}

        {/* Components Section */}
        {activeSection === 'components' && (
          <section className="space-y-2xl animate-fade-in">
            <div>
              <h2 className="text-3xl font-bold mb-lg text-primary">Components</h2>
              <p className="text-secondary mb-2xl">Composite components</p>
            </div>

            {/* Badges */}
            <div>
              <h3 className="text-xl font-semibold mb-lg text-primary">Badges</h3>
              <div className="flex flex-wrap gap-lg">
                <span className="badge badge-success">Success</span>
                <span className="badge badge-info">Info</span>
                <span className="badge badge-warning">Warning</span>
                <span className="badge badge-danger">Danger</span>
              </div>
            </div>

            {/* Progress Bar */}
            <div>
              <h3 className="text-xl font-semibold mb-lg text-primary">Progress</h3>
              <div className="space-y-md max-w-md">
                <div>
                  <div className="flex justify-between text-sm mb-md">
                    <span className="text-primary">Loading</span>
                    <span className="text-secondary">45%</span>
                  </div>
                  <div className="w-full h-1 bg-tertiary rounded-full overflow-hidden">
                    <div className="h-full w-[45%] bg-blue rounded-full transition-all duration-300" />
                  </div>
                </div>
              </div>
            </div>

            {/* Dividers */}
            <div>
              <h3 className="text-xl font-semibold mb-lg text-primary">Dividers</h3>
              <div className="space-y-lg">
                <div className="border-t border-primary" />
                <div className="flex items-center gap-lg">
                  <div className="flex-1 border-t border-primary" />
                  <span className="text-secondary text-sm">Or</span>
                  <div className="flex-1 border-t border-primary" />
                </div>
              </div>
            </div>

            {/* Alerts/Status Messages */}
            <div>
              <h3 className="text-xl font-semibold mb-lg text-primary">Status Messages</h3>
              <div className="space-y-lg max-w-md">
                <div className="bg-success/10 border border-success/30 rounded-lg p-lg flex gap-md">
                  <Zap className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-success">Success</p>
                    <p className="text-sm text-success/80">Your action was completed successfully</p>
                  </div>
                </div>
                <div className="bg-blue/10 border border-blue/30 rounded-lg p-lg flex gap-md">
                  <Eye className="w-5 h-5 text-blue flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-blue">Info</p>
                    <p className="text-sm text-blue/80">Here is some useful information</p>
                  </div>
                </div>
                <div className="bg-danger/10 border border-danger/30 rounded-lg p-lg flex gap-md">
                  <Eye className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-danger">Error</p>
                    <p className="text-sm text-danger/80">Something went wrong</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Spacing Scale */}
            <div>
              <h3 className="text-xl font-semibold mb-lg text-primary">Spacing Scale</h3>
              <div className="space-y-md">
                {['xs', 'sm', 'md', 'lg', 'xl', '2xl'].map((size) => (
                  <div key={size} className="flex items-center gap-4">
                    <span className="text-secondary text-sm w-12">{size}</span>
                    <div className={`h-8 bg-blue rounded p-${size}`}>
                      <div className="h-full bg-secondary rounded" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-primary bg-secondary mt-2xl">
        <div className="max-w-7xl mx-auto px-lg py-lg text-center text-secondary text-sm">
          <p>© 2025 Design System. Built with Tailwind CSS.</p>
        </div>
      </footer>
    </div>
  );
}