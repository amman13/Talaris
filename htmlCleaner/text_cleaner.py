#!/usr/bin/env python3
import os
from bs4 import BeautifulSoup

def clean_text(html_content):
    """
    Clean HTML content by removing unnecessary tags and attributes
    
    Args:
        html_content (str): Input HTML string
    
    Returns:
        str: Cleaned HTML string
    """
    # Create soup from HTML string
    soup = BeautifulSoup(html_content, 'html.parser')
    if not soup:
        return None

    # Clean tags
    for style_tag in soup.find_all('style'):
        style_tag.decompose()

    for script_tag in soup.find_all('script'):
        script_tag.decompose()

    for svg_tag in soup.find_all('svg'):
        for path_tag in svg_tag.find_all('path'):
            path_tag.decompose()

    # Clean attributes
    for tag in soup.find_all(True):
        attrs = dict(tag.attrs)
        new_attrs = {}
        
        if 'class' in attrs:
            new_attrs['class'] = attrs['class']
        for attr in attrs:
            if attr.startswith('data-v-'):
                new_attrs[attr] = attrs[attr]

        tag.attrs = new_attrs

    # Return cleaned HTML as string
    return soup.prettify()


def clean_html(input_path, output_path=None):
    """
    Clean an HTML file by removing style and script tags, paths within SVG elements,
    and keeping only class attributes and Vue.js identifiers.
    
    Args:
        input_path (str): Path to the input HTML file
        output_path (str, optional): Path to the output HTML file. If not provided, 
                                    will generate one based on the input filename.
    
    Returns:
        None
    """
    # If output path is not provided, create one based on input filename
    if not output_path:
        base_name = os.path.basename(input_path)
        file_name, file_ext = os.path.splitext(base_name)
        output_path = f"{file_name}_cleaned{file_ext}"
    
    try:
        # Read and parse the HTML file
        with open(input_path, 'r') as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        if not soup:
            print("Failed to parse HTML")
            return None
        
        # Remove all style tags
        for style_tag in soup.find_all('style'):
            style_tag.decompose()
        
        # Remove all script tags
        for script_tag in soup.find_all('script'):
            script_tag.decompose()
        
        # Remove <path> within <svg>
        for svg_tag in soup.find_all('svg'):
            for path_tag in svg_tag.find_all('path'):
                path_tag.decompose()
        
        # Clean attributes - only keep class and Vue.js identifiers
        for tag in soup.find_all(True): 
            attrs = dict(tag.attrs)
            new_attrs = {}
            
            # Keep class attributes
            if 'class' in attrs:
                new_attrs['class'] = attrs['class']
            
            # Keep Vue.js component identifiers (data-v-*)
            for attr in attrs:
                if attr.startswith('data-v-'):
                    new_attrs[attr] = attrs[attr]
            
            tag.attrs = new_attrs
        
        # Write the cleaned HTML to the output file
        cleaned_html = soup.prettify()
        with open(output_path, 'w') as file:
            file.write(cleaned_html)
        print(f"Cleaned HTML file saved to {output_path}")
        return None
    
    except Exception as e:
        print(f"Error processing HTML file: {e}")
        return None

