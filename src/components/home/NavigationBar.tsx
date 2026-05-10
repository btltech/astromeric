import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import './NavigationBar.css';

const primaryLinks = [
  { label: 'Home', to: '/', end: true },
  { label: 'Daily Insight', to: '/reading' },
  { label: 'Birth Chart', to: '/charts' },
  { label: 'Numerology', to: '/numerology' },
  { label: 'Compatibility', to: '/relationships' },
  { label: 'Year Ahead', to: '/year-ahead' },
  { label: 'Timing', to: '/tools' },
] as const;

const utilityLinks = [
  { label: 'Learn', to: '/learn' },
  { label: 'Profile', to: '/profile' },
  { label: 'Support', to: '/support' },
] as const;

export function NavigationBar() {
  const location = useLocation();
  const [menuOpen, setMenuOpen] = React.useState(false);
  const [theme, setTheme] = React.useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('astromeric_theme') as 'dark' | 'light') || 'dark';
  });

  React.useEffect(() => {
    if (theme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    localStorage.setItem('astromeric_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((t) => (t === 'light' ? 'dark' : 'light'));
  };

  React.useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  React.useEffect(() => {
    if (!menuOpen) {
      return undefined;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setMenuOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [menuOpen]);

  React.useEffect(() => {
    document.body.classList.toggle('nav-menu-open', menuOpen);
    return () => document.body.classList.remove('nav-menu-open');
  }, [menuOpen]);

  return (
    <header className="topbar">
      <div className="topbar__inner">
        <div className="topbar__brand-block">
          <NavLink to="/" className="topbar__brand" aria-label="AstroNumeric home">
            Astro<span>Numeric</span>
          </NavLink>
        </div>

        <button
          type="button"
          className="topbar__toggle"
          aria-expanded={menuOpen}
          aria-controls="primary-navigation"
          aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
          onClick={() => setMenuOpen((open) => !open)}
        >
          {menuOpen ? 'Close' : 'Menu'}
        </button>

        <nav
          id="primary-navigation"
          className={`topbar__nav${menuOpen ? ' topbar__nav--open' : ''}`}
          aria-label="Primary navigation"
        >
          <div className="topbar__nav-links">
            {primaryLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.end}
                className={({ isActive }) => {
                  const active = isActive || (link.to === '/charts' && location.pathname === '/experience');
                  return active ? 'topbar__link topbar__link--active' : 'topbar__link';
                }}
              >
                {link.label}
              </NavLink>
            ))}
          </div>

          <div className="topbar__mobile-utility">
            {utilityLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  isActive ? 'topbar__utility-link topbar__utility-link--active' : 'topbar__utility-link'
                }
              >
                {link.label}
              </NavLink>
            ))}
            <button 
              className="topbar__theme-toggle" 
              onClick={toggleTheme}
              aria-label="Toggle theme"
            >
              {theme === 'light' ? '☾ Dark Mode' : '☀️ Light Mode'}
            </button>
          </div>
        </nav>

        <div className="topbar__utility">
          {utilityLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                isActive ? 'topbar__utility-link topbar__utility-link--active' : 'topbar__utility-link'
              }
            >
              {link.label}
            </NavLink>
          ))}
          <button 
            className="topbar__theme-toggle-icon" 
            onClick={toggleTheme}
            aria-label="Toggle theme"
            title="Toggle theme"
          >
            {theme === 'light' ? '☾' : '☀️'}
          </button>
        </div>
      </div>
    </header>
  );
}
