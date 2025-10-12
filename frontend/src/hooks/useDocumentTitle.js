import { useEffect } from 'react';

/**
 * Custom hook to update document title
 * @param {string} title - The page title
 * @param {boolean} includeAppName - Whether to include app name suffix
 */
export function useDocumentTitle(title, includeAppName = true) {
  useEffect(() => {
    const appName = 'Smart Campus';
    document.title = includeAppName ? `${title} | ${appName}` : title;
    
    // Cleanup: restore default title when component unmounts
    return () => {
      document.title = `${appName} - Doc Scanner & Management`;
    };
  }, [title, includeAppName]);
}

export default useDocumentTitle;
