<template>
  <div class="bg-white rounded-lg shadow-lg border border-gray-200 w-80">
    <!-- Search -->
    <div class="p-2 border-b border-gray-100">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search emoji..."
        class="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>

    <!-- Categories -->
    <div class="flex border-b border-gray-100 px-2">
      <button
        v-for="category in categories"
        :key="category.name"
        @click="activeCategory = category.name"
        :class="[
          'p-2 text-lg hover:bg-gray-100 rounded transition-colors',
          activeCategory === category.name ? 'bg-gray-100' : ''
        ]"
        :title="category.name"
      >
        {{ category.icon }}
      </button>
    </div>

    <!-- Emoji Grid -->
    <div class="h-48 overflow-y-auto p-2">
      <!-- Recent -->
      <div v-if="!searchQuery && recentEmojis.length > 0" class="mb-4">
        <p class="text-xs font-medium text-gray-500 mb-2 px-1">Recent</p>
        <div class="grid grid-cols-8 gap-1">
          <button
            v-for="emoji in recentEmojis"
            :key="emoji"
            @click="selectEmoji(emoji)"
            class="p-1.5 text-xl hover:bg-gray-100 rounded transition-colors"
          >
            {{ emoji }}
          </button>
        </div>
      </div>

      <!-- Search Results -->
      <div v-if="searchQuery">
        <p class="text-xs font-medium text-gray-500 mb-2 px-1">Results</p>
        <div v-if="filteredEmojis.length > 0" class="grid grid-cols-8 gap-1">
          <button
            v-for="emoji in filteredEmojis"
            :key="emoji.emoji"
            @click="selectEmoji(emoji.emoji)"
            class="p-1.5 text-xl hover:bg-gray-100 rounded transition-colors"
            :title="emoji.name"
          >
            {{ emoji.emoji }}
          </button>
        </div>
        <p v-else class="text-sm text-gray-500 text-center py-4">No emojis found</p>
      </div>

      <!-- Category Emojis -->
      <div v-else>
        <p class="text-xs font-medium text-gray-500 mb-2 px-1">{{ activeCategory }}</p>
        <div class="grid grid-cols-8 gap-1">
          <button
            v-for="emoji in categoryEmojis"
            :key="emoji.emoji"
            @click="selectEmoji(emoji.emoji)"
            class="p-1.5 text-xl hover:bg-gray-100 rounded transition-colors"
            :title="emoji.name"
          >
            {{ emoji.emoji }}
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Reactions (for message reactions) -->
    <div v-if="showQuickReactions" class="flex justify-center space-x-1 p-2 border-t border-gray-100 bg-gray-50 rounded-b-lg">
      <button
        v-for="emoji in quickReactions"
        :key="emoji"
        @click="selectEmoji(emoji)"
        class="p-2 text-xl hover:bg-gray-200 rounded-full transition-colors"
      >
        {{ emoji }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"

const props = defineProps({
	showQuickReactions: { type: Boolean, default: false },
})

const emit = defineEmits(["select"])

const searchQuery = ref("")
const activeCategory = ref("Smileys")
const recentEmojis = ref([])

const quickReactions = ["👍", "❤️", "😂", "😮", "😢", "🙏"]

const categories = [
	{ name: "Smileys", icon: "😀" },
	{ name: "People", icon: "👋" },
	{ name: "Nature", icon: "🐱" },
	{ name: "Food", icon: "🍕" },
	{ name: "Activities", icon: "⚽" },
	{ name: "Travel", icon: "🚗" },
	{ name: "Objects", icon: "💡" },
	{ name: "Symbols", icon: "❤️" },
]

// Common emojis by category
const emojiData = {
	Smileys: [
		{ emoji: "😀", name: "grinning face" },
		{ emoji: "😃", name: "grinning face with big eyes" },
		{ emoji: "😄", name: "grinning face with smiling eyes" },
		{ emoji: "😁", name: "beaming face" },
		{ emoji: "😅", name: "grinning face with sweat" },
		{ emoji: "😂", name: "face with tears of joy" },
		{ emoji: "🤣", name: "rolling on the floor laughing" },
		{ emoji: "😊", name: "smiling face with smiling eyes" },
		{ emoji: "😇", name: "smiling face with halo" },
		{ emoji: "🙂", name: "slightly smiling face" },
		{ emoji: "😉", name: "winking face" },
		{ emoji: "😌", name: "relieved face" },
		{ emoji: "😍", name: "smiling face with heart-eyes" },
		{ emoji: "🥰", name: "smiling face with hearts" },
		{ emoji: "😘", name: "face blowing a kiss" },
		{ emoji: "😋", name: "face savoring food" },
		{ emoji: "😜", name: "winking face with tongue" },
		{ emoji: "🤪", name: "zany face" },
		{ emoji: "😎", name: "smiling face with sunglasses" },
		{ emoji: "🤓", name: "nerd face" },
		{ emoji: "🤔", name: "thinking face" },
		{ emoji: "🤨", name: "face with raised eyebrow" },
		{ emoji: "😐", name: "neutral face" },
		{ emoji: "😑", name: "expressionless face" },
		{ emoji: "😶", name: "face without mouth" },
		{ emoji: "🙄", name: "face with rolling eyes" },
		{ emoji: "😏", name: "smirking face" },
		{ emoji: "😣", name: "persevering face" },
		{ emoji: "😥", name: "sad but relieved face" },
		{ emoji: "😮", name: "face with open mouth" },
		{ emoji: "🤐", name: "zipper-mouth face" },
		{ emoji: "😯", name: "hushed face" },
	],
	People: [
		{ emoji: "👋", name: "waving hand" },
		{ emoji: "🤚", name: "raised back of hand" },
		{ emoji: "🖐️", name: "hand with fingers splayed" },
		{ emoji: "✋", name: "raised hand" },
		{ emoji: "👌", name: "OK hand" },
		{ emoji: "🤌", name: "pinched fingers" },
		{ emoji: "✌️", name: "victory hand" },
		{ emoji: "🤞", name: "crossed fingers" },
		{ emoji: "🤟", name: "love-you gesture" },
		{ emoji: "🤘", name: "sign of the horns" },
		{ emoji: "👍", name: "thumbs up" },
		{ emoji: "👎", name: "thumbs down" },
		{ emoji: "👏", name: "clapping hands" },
		{ emoji: "🙌", name: "raising hands" },
		{ emoji: "👐", name: "open hands" },
		{ emoji: "🤲", name: "palms up together" },
		{ emoji: "🤝", name: "handshake" },
		{ emoji: "🙏", name: "folded hands" },
		{ emoji: "💪", name: "flexed biceps" },
		{ emoji: "🦾", name: "mechanical arm" },
		{ emoji: "👂", name: "ear" },
		{ emoji: "👀", name: "eyes" },
		{ emoji: "👁️", name: "eye" },
		{ emoji: "🧠", name: "brain" },
	],
	Nature: [
		{ emoji: "🐱", name: "cat face" },
		{ emoji: "🐶", name: "dog face" },
		{ emoji: "🐭", name: "mouse face" },
		{ emoji: "🐹", name: "hamster" },
		{ emoji: "🐰", name: "rabbit face" },
		{ emoji: "🦊", name: "fox" },
		{ emoji: "🐻", name: "bear" },
		{ emoji: "🐼", name: "panda" },
		{ emoji: "🐨", name: "koala" },
		{ emoji: "🦁", name: "lion" },
		{ emoji: "🐯", name: "tiger face" },
		{ emoji: "🦄", name: "unicorn" },
		{ emoji: "🌸", name: "cherry blossom" },
		{ emoji: "🌺", name: "hibiscus" },
		{ emoji: "🌻", name: "sunflower" },
		{ emoji: "🌹", name: "rose" },
		{ emoji: "🌳", name: "deciduous tree" },
		{ emoji: "🌴", name: "palm tree" },
		{ emoji: "🌵", name: "cactus" },
		{ emoji: "☀️", name: "sun" },
		{ emoji: "🌙", name: "crescent moon" },
		{ emoji: "⭐", name: "star" },
		{ emoji: "🌈", name: "rainbow" },
		{ emoji: "🔥", name: "fire" },
	],
	Food: [
		{ emoji: "🍕", name: "pizza" },
		{ emoji: "🍔", name: "hamburger" },
		{ emoji: "🍟", name: "french fries" },
		{ emoji: "🌭", name: "hot dog" },
		{ emoji: "🍿", name: "popcorn" },
		{ emoji: "🍩", name: "doughnut" },
		{ emoji: "🍪", name: "cookie" },
		{ emoji: "🎂", name: "birthday cake" },
		{ emoji: "🍰", name: "shortcake" },
		{ emoji: "🍫", name: "chocolate bar" },
		{ emoji: "🍬", name: "candy" },
		{ emoji: "☕", name: "coffee" },
		{ emoji: "🍵", name: "tea" },
		{ emoji: "🍺", name: "beer" },
		{ emoji: "🥤", name: "cup with straw" },
		{ emoji: "🍎", name: "red apple" },
		{ emoji: "🍊", name: "orange" },
		{ emoji: "🍋", name: "lemon" },
		{ emoji: "🍇", name: "grapes" },
		{ emoji: "🍓", name: "strawberry" },
		{ emoji: "🥑", name: "avocado" },
		{ emoji: "🥕", name: "carrot" },
		{ emoji: "🌽", name: "corn" },
		{ emoji: "🍗", name: "poultry leg" },
	],
	Activities: [
		{ emoji: "⚽", name: "soccer ball" },
		{ emoji: "🏀", name: "basketball" },
		{ emoji: "🏈", name: "football" },
		{ emoji: "⚾", name: "baseball" },
		{ emoji: "🎾", name: "tennis" },
		{ emoji: "🏐", name: "volleyball" },
		{ emoji: "🏉", name: "rugby" },
		{ emoji: "🎱", name: "8 ball" },
		{ emoji: "🏓", name: "ping pong" },
		{ emoji: "🎯", name: "bullseye" },
		{ emoji: "🎮", name: "video game" },
		{ emoji: "🎲", name: "game die" },
		{ emoji: "🎭", name: "performing arts" },
		{ emoji: "🎨", name: "artist palette" },
		{ emoji: "🎬", name: "clapper board" },
		{ emoji: "🎤", name: "microphone" },
		{ emoji: "🎧", name: "headphone" },
		{ emoji: "🎸", name: "guitar" },
		{ emoji: "🎹", name: "piano" },
		{ emoji: "🎺", name: "trumpet" },
		{ emoji: "🏆", name: "trophy" },
		{ emoji: "🥇", name: "gold medal" },
		{ emoji: "🎖️", name: "military medal" },
		{ emoji: "🏅", name: "sports medal" },
	],
	Travel: [
		{ emoji: "🚗", name: "car" },
		{ emoji: "🚕", name: "taxi" },
		{ emoji: "🚌", name: "bus" },
		{ emoji: "🚎", name: "trolleybus" },
		{ emoji: "🏎️", name: "racing car" },
		{ emoji: "🚓", name: "police car" },
		{ emoji: "🚑", name: "ambulance" },
		{ emoji: "🚒", name: "fire engine" },
		{ emoji: "✈️", name: "airplane" },
		{ emoji: "🚀", name: "rocket" },
		{ emoji: "🚁", name: "helicopter" },
		{ emoji: "🛸", name: "flying saucer" },
		{ emoji: "🚂", name: "locomotive" },
		{ emoji: "🚢", name: "ship" },
		{ emoji: "⛵", name: "sailboat" },
		{ emoji: "🏠", name: "house" },
		{ emoji: "🏢", name: "office building" },
		{ emoji: "🏥", name: "hospital" },
		{ emoji: "🏫", name: "school" },
		{ emoji: "🏰", name: "castle" },
		{ emoji: "🗼", name: "Tokyo tower" },
		{ emoji: "🗽", name: "Statue of Liberty" },
		{ emoji: "🌍", name: "globe Europe-Africa" },
		{ emoji: "🗺️", name: "world map" },
	],
	Objects: [
		{ emoji: "💡", name: "light bulb" },
		{ emoji: "🔦", name: "flashlight" },
		{ emoji: "📱", name: "mobile phone" },
		{ emoji: "💻", name: "laptop" },
		{ emoji: "🖥️", name: "desktop computer" },
		{ emoji: "🖨️", name: "printer" },
		{ emoji: "⌨️", name: "keyboard" },
		{ emoji: "🖱️", name: "mouse" },
		{ emoji: "📷", name: "camera" },
		{ emoji: "🎥", name: "movie camera" },
		{ emoji: "📞", name: "telephone receiver" },
		{ emoji: "📺", name: "television" },
		{ emoji: "📻", name: "radio" },
		{ emoji: "⏰", name: "alarm clock" },
		{ emoji: "🔑", name: "key" },
		{ emoji: "🔒", name: "locked" },
		{ emoji: "🔓", name: "unlocked" },
		{ emoji: "📝", name: "memo" },
		{ emoji: "📎", name: "paperclip" },
		{ emoji: "📌", name: "pushpin" },
		{ emoji: "📁", name: "file folder" },
		{ emoji: "📊", name: "bar chart" },
		{ emoji: "📈", name: "chart increasing" },
		{ emoji: "📉", name: "chart decreasing" },
	],
	Symbols: [
		{ emoji: "❤️", name: "red heart" },
		{ emoji: "🧡", name: "orange heart" },
		{ emoji: "💛", name: "yellow heart" },
		{ emoji: "💚", name: "green heart" },
		{ emoji: "💙", name: "blue heart" },
		{ emoji: "💜", name: "purple heart" },
		{ emoji: "🖤", name: "black heart" },
		{ emoji: "🤍", name: "white heart" },
		{ emoji: "💔", name: "broken heart" },
		{ emoji: "💯", name: "hundred points" },
		{ emoji: "✅", name: "check mark" },
		{ emoji: "❌", name: "cross mark" },
		{ emoji: "⭕", name: "hollow circle" },
		{ emoji: "❓", name: "question mark" },
		{ emoji: "❗", name: "exclamation mark" },
		{ emoji: "💤", name: "zzz" },
		{ emoji: "💢", name: "anger symbol" },
		{ emoji: "💥", name: "collision" },
		{ emoji: "💫", name: "dizzy" },
		{ emoji: "💬", name: "speech balloon" },
		{ emoji: "👁️‍🗨️", name: "eye in speech bubble" },
		{ emoji: "🔴", name: "red circle" },
		{ emoji: "🟢", name: "green circle" },
		{ emoji: "🔵", name: "blue circle" },
	],
}

const categoryEmojis = computed(() => emojiData[activeCategory.value] || [])

const filteredEmojis = computed(() => {
	if (!searchQuery.value) return []
	const query = searchQuery.value.toLowerCase()
	return Object.values(emojiData)
		.flat()
		.filter((e) => e.name.includes(query))
})

const selectEmoji = (emoji) => {
	// Update recent emojis
	const recent = recentEmojis.value.filter((e) => e !== emoji)
	recent.unshift(emoji)
	recentEmojis.value = recent.slice(0, 16)
	localStorage.setItem(
		"mkaguzi_recent_emojis",
		JSON.stringify(recentEmojis.value),
	)

	emit("select", emoji)
}

onMounted(() => {
	const stored = localStorage.getItem("mkaguzi_recent_emojis")
	if (stored) {
		try {
			recentEmojis.value = JSON.parse(stored)
		} catch (e) {
			// ignore
		}
	}
})
</script>
