<template>
	<div
		v-if="!showInstruction"
		class="instruction-container"
	>
		<BaseButton
			v-if="!isLoadingInstructions"
			class="direction-button"
			@click="toggleInput"
		>
			<Icon icon="graduation-cap" />
		</BaseButton>
		<Icon
			v-if="isLoadingInstructions"
			class="direction-button"
			icon="hourglass-half"
		/>
		<div
			v-if="isInputOpen"
			class="query-container"
		>
			<input
				v-model="queryInput"
				type="text"
				placeholder="What would you like to do..."
			>
			<BaseButton
				class="direction-button"
				@click="handleChatInput"
			>
				<Icon icon="arrow-right" />
			</BaseButton>
		</div>
	</div>
	<div
		v-if="showInstruction"
		class="instruction-container"
	>
		<BaseButton
			v-if="instructionStep > 0"
			class="direction-button"
			@click="showPrevInstruction"
		>
			<Icon icon="angle-left" />
		</BaseButton>
		<p>
			{{ currentInstruction }}
		</p>
		<BaseButton
			class="direction-button"
			@click="clickRedBoxedElements"
		>
			<Icon icon="wand-magic" />
		</BaseButton>
		<BaseButton
			v-if="!isLastInstructionStep"
			class="direction-button"
			@click="showNextInstruction"
		>
			<Icon icon="angle-right" />
		</BaseButton>
		<BaseButton
			v-if="isLastInstructionStep"
			class="direction-button"
			@click="showNextInstruction"
		>
			<Icon icon="check" />
		</BaseButton>
	</div>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import BaseButton from '@/components/base/BaseButton.vue'

import axios from 'axios'
import { cleanHtmlText, extractTextContent } from '../../../../htmlCleaner/text_cleaner.js'
import { OPENAI_API_KEY } from '../../open-ai.config.js'
import { system_prompt, other_pages_prompt, additional_other_pages_prompt } from './DropoutChat.config.js'

const route = useRoute()

const currentRouteUrl = ref(route.fullPath)

watch(route, (newRoute) => {
    const element = document.documentElement
    const extractedText = extractTextContent(element)
    const pageUrl = currentRouteUrl.value

	console.log(extractedText)
	console.log('Page URL')
	console.log(pageUrl)

    // Save the extracted text and URL of the current page
    savePageData(pageUrl, extractedText)

    // Update the current route URL to the new route
    currentRouteUrl.value = newRoute.fullPath
	console.log('New Route URL')
	console.log(currentRouteUrl.value)
})

function savePageData(url: string, extractedText: string) {
	const storageKey = 'pageData'
    const storedData = localStorage.getItem(storageKey)
    const pageData = storedData ? JSON.parse(storedData) : {}

    // Update or add the cleaned HTML for the current URL
    pageData[url] = extractedText

    // Save the updated data back to local storage
    localStorage.setItem(storageKey, JSON.stringify(pageData))
	console.log(`Data saved for URL: ${url}`)

}

const queryInput = ref('')

const isInputOpen = ref(false)
const showInstruction = ref(false)
const currentInstruction = ref('')
const instructionStep = ref(0)

const isLoadingInstructions = ref(false)
const isLastInstructionStep = computed(() => instructionStep.value == instructionSet.length - 1)

let instructionSet: []

const toggleInput = () => {
	isInputOpen.value = !isInputOpen.value
}

const handleChatInput = async () => {
	toggleInput()
	isLoadingInstructions.value = true

	const userMessage = queryInput.value
	console.log(`Query from user: ${userMessage}`)
	queryInput.value = ''

	const element = document.documentElement 
	const cleanedHtml = cleanHtmlText(element)
	console.log(cleanedHtml)

	// Retrieve stored page data
	const storageKey = 'pageData'
    const storedData = localStorage.getItem(storageKey)
    const pageData = storedData ? JSON.parse(storedData) : {}

    // Extract text content from all stored pages
    let otherPagesText = 'Here is what the other pages look like:\n'
    for (const [url, pageText] of Object.entries(pageData)) {
        otherPagesText += `URL: ${url}\n${pageText}\n${url}\n---\n`
    }
	if (otherPagesText.length > 10000) {
		otherPagesText = otherPagesText.substring(0, 10000)
	}
	otherPagesText += other_pages_prompt
	console.log(otherPagesText)

	try {
		const response = await axios.post('https://api.openai.com/v1/responses', {
			model: 'gpt-4o-mini',
			input: [
				{
					role: 'system',
					content: [
						{
							type: 'input_text',
							text: system_prompt,
						},
					],
				},
				{
					role: 'user',
					content: [
						{
							type: 'input_text',
							text: `${otherPagesText}\n${cleanedHtml}\n${userMessage}\n\n${additional_other_pages_prompt}`,
						},
					],
				},
			],
			text: {
				format: {
					type: 'text',
				},
			},
			reasoning: {},
			tools: [],
			temperature: 1,
			max_output_tokens: 1000,
			top_p: 1,
			store: true,
		}, {
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${OPENAI_API_KEY}`,
			},
		})

		isLoadingInstructions.value = false
		const aiResponse = response.data.output[0].content[0].text
		console.log(`Response from OpenAI: ${aiResponse}`)

		const startIndex = aiResponse.indexOf('[')
		const endIndex = aiResponse.lastIndexOf(']')
		
		const jsonResponse = aiResponse.substring(startIndex, endIndex + 1)
		
		instructionSet = JSON.parse(jsonResponse)
		instructionStep.value = -1
		showNextInstruction()
		showInstruction.value = true

	} catch (error) {
		console.error('Error fetching AI response:', error)
	}
}

function showPrevInstruction() {
	showInstructionIn(-1)
}
function showNextInstruction() {
	showInstructionIn(1)
}

function showInstructionIn(direction:number) {
	clearHighlightElement()

	if (instructionSet.length == instructionStep.value+direction) {
		showInstruction.value = false
	} else {
		console.log('Showing instruction...')
		instructionStep.value+=direction

		const step = instructionSet[instructionStep.value]
		
		console.log(`Showing - ${step}`)
		const cleanedItem = JSON.stringify(step).replace(/[`]/g, '').replace(/json/g, '').replace(/'/g, '').trim()
		highlightElement(cleanedItem)
	}
}

function clearHighlightElement() {
	const redBoxes = document.querySelectorAll('.red-box')
	redBoxes.forEach(box => {
		box.classList.remove('red-box')
	})
}

function highlightElement(cleanedResponse: string) {
	console.log(cleanedResponse)
	try {
		// Parse the cleaned response
		const parsedResponse = JSON.parse(cleanedResponse)
		// Extract the necessary information
		const { instruction, attributes, tag, textContent } = parsedResponse
		console.log(instruction, attributes, tag, textContent)
		
		currentInstruction.value = instruction

		let attributeSelectors = ''

		// Check if attributes is an object
		if (typeof attributes === 'object' && attributes !== null) {
			attributeSelectors = Object.entries(attributes)
				.map(([key, value]) => {
					if (key === 'class' && value.trim() !== '') {
						// Handle multiple classes
						return value.split(' ').map((cls: string) => `.${cls}`).join('')
					} else if (key !== 'class') {
						return `[${key}="${value}"]`
					}
					return '' // Return an empty string if class is empty
				})
				.join('')
		} else {
			console.warn('Attributes is not an object:', attributes)
		}

		console.log('Attribute Selectors')
		console.log(attributeSelectors)

		const selector = `${tag}${attributeSelectors}`
		console.log('Selector')
		console.log(selector)

		// Find elements that match the text content
		let matchingElements = Array.from(document.querySelectorAll('*')).filter(element => {
			return element.textContent?.trim() === textContent
		})

		// If no elements match the text content, select all elements with the tag
		if (matchingElements.length === 0 || !textContent.trim())  {
			matchingElements = Array.from(document.querySelectorAll(tag))
		}

		// Split the selector into individual selectors
		const individualSelectors = selector.split(/(?=\[)|(?=\.)/)

		// Filter elements by each selector one at a time
		individualSelectors.forEach(sel => {
			try {
				if (matchingElements.length > 1) {
					const previousMatchingElements = [...matchingElements]
					matchingElements = matchingElements.filter(element => element.matches(`${tag}${sel}`))
					// If filtering results in no elements, revert to the previous state
					if (matchingElements.length === 0) {
						matchingElements = previousMatchingElements
					}
				}
			} catch (error) {
				console.error(`Invalid selector: ${sel}`, error)
			}
		})
		if (matchingElements.length > 1) {
			matchingElements = [matchingElements[0]]
		}

		// Highlight the matching elements, can be 0 or 1
		matchingElements.forEach(element => {
			element.classList.add('red-box')
			console.log(`Element with text "${textContent}" highlighted.`)
		})

	} catch (error) {
		console.error('Failed to parse AI response:', error)
	}
}

const clickRedBoxedElements = () => {
	const redBoxedElements = document.querySelectorAll('.red-box')
	redBoxedElements.forEach(element => {
		(element as HTMLElement).click()
	})
}
</script>

<style lang="scss" scoped>
.red-box {
	border: 3px solid #ff7d00 !important;
	/* Ensure the border is applied */
	padding: 5px !important;
	/* Ensure padding is applied */
	z-index: 1000 !important;
	/* Ensure it appears above other elements */
}

.instruction-container {
	position: fixed;
	// FIXME: We should prevent usage of z-index or
	// at least define it centrally
	// the highest z-index of a modal is .hint-modal with 4500
	z-index: 5000;
	bottom: 1rem;
	inset-inline: 1rem;
	max-width: max-content;
	margin-inline: auto;

	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 1rem;
	padding: .5rem 1rem;
	background: var(--grey-900);
	border-radius: $radius;
	font-size: .9rem;
	color: var(--grey-200);
}

.query-container input[type=text] {
  background: var(--grey-900);
  box-sizing: border-box;
  border: none;
  border-bottom: 2px solid var(--grey-200);
}

.direction-button {
	padding: .25rem .5rem;
	cursor: pointer;
}
</style>