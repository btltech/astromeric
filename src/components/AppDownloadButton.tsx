import React from 'react';

import { APP_STORE_LIVE, APP_STORE_URL, GOOGLE_PLAY_URL } from '../config/appLinks';

type Store = 'app-store' | 'google-play';

interface Props {
  store: Store;
  className?: string;
  style?: React.CSSProperties;
}

const APPLE_ICON =
  'M18.71,19.5C17.88,20.74 17,21.95 15.66,22C14.32,22.05 13.89,21.24 12.37,21.24C10.84,21.24 10.37,21.97 9.1,22C7.79,22.05 6.8,20.68 5.96,19.47C4.25,17 2.94,12.45 4.7,9.39C5.57,7.87 7.13,6.91 8.82,6.88C10.1,6.86 11.32,7.75 12.11,7.75C12.89,7.75 14.37,6.68 15.92,6.84C16.57,6.87 18.39,7.1 19.56,8.82C19.47,8.88 17.39,10.1 17.41,12.63C17.44,15.65 20.06,16.66 20.1,16.67C20.08,16.74 19.67,18.11 18.71,19.5M15.97,4.17C16.63,3.37 17.07,2.28 16.95,1C16,1.04 14.9,1.6 14.24,2.38C13.68,3.04 13.19,4.14 13.34,5.39C14.39,5.47 15.4,4.88 15.97,4.17Z';
const PLAY_ICON =
  'M5,3.14L15.42,13.56L18.43,10.55C19.06,9.92 19.06,8.9 18.43,8.27L15.34,5.18C14.07,3.91 12.02,3.91 10.75,5.18L5,3.14M16.5,14.64L6.07,4.21L3.14,7.14C2.5,7.78 2.5,8.8 3.14,9.43L6.23,12.53C7.5,13.8 9.55,13.8 10.82,12.53L16.5,14.64M11.9,11.38L21.31,20.79C21.94,20.16 21.94,19.14 21.31,18.51L18.22,15.42C16.95,14.15 14.9,14.15 13.63,15.42L11.9,11.38M20.21,22L9.79,11.58L6.78,14.59C6.15,15.22 6.15,16.24 6.78,16.87L9.87,19.96C11.14,21.23 13.19,21.23 14.46,19.96L20.21,22Z';

/**
 * A store button. It links to the store once the app is there and otherwise
 * reads "Coming soon", so nobody lands on a missing page.
 */
export function AppDownloadButton({ store, className, style }: Props) {
  const isApple = store === 'app-store';
  const href = isApple ? (APP_STORE_LIVE ? APP_STORE_URL : null) : GOOGLE_PLAY_URL;
  const storeName = isApple ? 'App Store' : 'Google Play';
  const label = href ? `Get it on the ${storeName}` : `Coming soon to ${storeName}`;

  const content = (
    <>
      <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="currentColor"
        aria-hidden="true"
        style={{ marginTop: '-2px' }}
      >
        <path d={isApple ? APPLE_ICON : PLAY_ICON} />
      </svg>
      {label}
    </>
  );

  if (!href) {
    return (
      <span className={className} style={{ ...style, cursor: 'default', opacity: 0.75 }}>
        {content}
      </span>
    );
  }
  return (
    <a className={className} style={style} href={href} target="_blank" rel="noopener noreferrer">
      {content}
    </a>
  );
}
