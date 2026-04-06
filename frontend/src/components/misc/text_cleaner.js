/**
 * Main: Clean HTML by keeping only body content and removing all SVG elements
 *
 * @param {Element} domElement - Input DOM element
 * @returns {string} Cleaned HTML string
 */
export function cleanHtmlText(domElement) {
	if (!domElement) return null;

	// Create a clone to avoid modifying the original
	const doc = domElement.cloneNode(true);

	// Keep only the body content if it exists
	const body = doc.querySelector('body');
	if (body) {
		// Clear the document and append only the body content
		while (doc.firstChild) {
			doc.removeChild(doc.firstChild);
		}
		doc.appendChild(body);
	}

	// Remove <style> tags
	doc.querySelectorAll('style').forEach(style => style.remove());

	// Remove <script> tags
	doc.querySelectorAll('script').forEach(script => script.remove());

	// Keep only <title> and <desc> tags inside SVG, remove all other tags inside SVG
	doc.querySelectorAll('svg').forEach(svg => {
		const titleElement = svg.querySelector('title');
		const descElement = svg.querySelector('desc');
		
		// Clear all content of SVG
		while (svg.firstChild) {
			svg.removeChild(svg.firstChild);
		}
		
		// Add back only title and desc if they existed
		if (titleElement) {
			svg.appendChild(titleElement);
		}
		if (descElement) {
			svg.appendChild(descElement);
		}
	});

	return doc.outerHTML
		.replace(/>\s+</g, '><') // Remove whitespace between tags
		.replace(/\s{2,}/g, ' ') // Replace multiple spaces with single space
		.trim();
}


export function extractTextContent(domElement) {
    if (!domElement) return '';

    // Use a recursive function to gather text content
    const getTextContent = (node) => {
        let text = '';
        node.childNodes.forEach(child => {
            if (child.nodeType === Node.TEXT_NODE) {
                text += child.textContent.trim() + ' ';
            } else if (child.nodeType === Node.ELEMENT_NODE) {
                // Skip <style> and <script> elements
                if (child.tagName.toLowerCase() !== 'style' && child.tagName.toLowerCase() !== 'script') {
                    text += getTextContent(child);
                }
            }
        });
        return text;
    };

    return getTextContent(domElement).trim();
}

// Example usage with the entire document
// const element = document.documentElement; const cleanedHtml = cleanHtmlText(element); console.log(cleanedHtml);
