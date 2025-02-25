// Function to fetch the base URL from config.txt
function fetchBaseUrl() {
    return fetch('config.txt') // Path to the .txt file
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch config.txt');
            }
            return response.text();
        })
        .then(url => url.trim()); // Trim to avoid whitespace issues
}

document.getElementById('lootForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    // Get the base URL first
    const baseUrl = await fetchBaseUrl();  // Use await to ensure this completes first
    console.log('Fetched Base URL:', baseUrl);

    // Get form data
    const formData = new FormData(event.target);
    const lootType = formData.get('lootType'); // Get the loot type from radio buttons
    const crValue = formData.get('crValue');  // Get the CR value from input field

    // Log to check values
    console.log('Loot Type:', lootType);
    console.log('CR Value:', crValue);

    // Validate CR value
    if (isNaN(crValue) || crValue < 0 || crValue > 99) {
        alert("Please enter a valid CR value between 0 and 17.");
        return;
    }

    try {
        // Send POST request to Flask API
        const response = await fetch(`${baseUrl}/get_loot`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ loot_type: lootType, cr_value: crValue }),
        });

        const resultsDiv = document.getElementById('result');
        resultsDiv.innerHTML = ''; // Clear previous results

        if (response.ok) {
            const data = await response.json();

            // Display loot results based on type
            if (lootType === 'hoard') {
                let formattedCoins = '';
                let formattedArt = '';
                let formattedGems = '';
                let formattedMagicItems = '';

                if (Array.isArray(data.coins)) {
                    data.coins.forEach(coins => {
                        // Check if cash entry contains both amount and coin type
                        const [amount, coinType] = coins.split(' ');

                        // Format the amount if it's a valid number
                        let formattedAmount = amount;
                        if (!isNaN(parseInt(amount)) && parseInt(amount) >= 1000) {
                            // Format the amount (e.g., "18000" -> "18,000")
                            formattedAmount = amount.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
                        }

                        // Append the formatted cash entry (e.g., "18,000 gp" or "300 sp")
                        formattedCoins += `<li>${formattedAmount} ${coinType}</li>`;
                    });
                } else {
                    formattedCoins = '<li>No cash available</li>'; // Handle case if there's no cash data
                }
                                
                // Output the result (for example purposes)
                console.log(formattedCoins);
                // Format art objects (check if art exists and is an array)
                if (Array.isArray(data.selected_art) && data.selected_art.length > 0) {
                    data.selected_art.forEach(art => {
                        formattedArt += `<li>${art}</li>`;
                    });
                } else {
                    formattedArt = '<li>No art objects found</li>'; // Fallback if no art objects
                }

                // Format gems (check if gems exists and is an array)
                if (Array.isArray(data.selected_gems) && data.selected_gems.length > 0) {
                    data.selected_gems.forEach(gem => {
                        formattedGems += `<li>${gem}</li>`;
                    });
                } else {
                    formattedGems = '<li>No gems found</li>'; // Fallback if no gems
                }

                // Format magic items (check if magic_items exists and is an array)
                if (Array.isArray(data.magic_items) && data.magic_items.length > 0) {
                    data.magic_items.forEach(item => {
                        formattedMagicItems += `<li>${item}</li>`;
                    });
                } else {
                    formattedMagicItems = '<li>No magic items found</li>'; // Fallback if no magic items
                }

                resultsDiv.innerHTML = `
                    <h3>Hoard Loot:</h3>
                    <p><strong>Coins:</strong></p>
                    <ul>${formattedCoins}</ul>
                    <p><strong>Art Objects:</strong></p>
                    <ul>${formattedArt}</ul>
                    <p><strong>Gems:</strong></p>
                    <ul>${formattedGems}</ul>
                    <p><strong>Magic Items:</strong></p>
                    <ul>${formattedMagicItems}</ul>
                `;
            } else if (lootType === 'individual') {
                let formattedCash = '';
                
                if (Array.isArray(data.cash)) {
                    data.cash.forEach(cash => {
                        if (typeof cash === 'string') {
                            let formattedCashPart = cash.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1 ');
                            formattedCash += `<li>${formattedCashPart}</li>`;
                        } else {
                            formattedCash += `<li>${cash}</li>`; 
                        }
                    });
                }
                    // <p><strong>Cash:</strong></p>

                resultsDiv.innerHTML = `
                    <h3>Individual Loot: </h3>
                    <bold>(Hard cash / Ingredients / Trophies)  </bold>
                    <ul>
                        ${formattedCash}
                    </ul>
                `;
            }
        } else {
            // If there's an error, display it
            const error = await response.json();
            resultsDiv.innerHTML = `<h3>Error:</h3><p>${error.error}</p>`;
        }
    } catch (error) {
        // Handle any errors that occur during the fetch
        console.error('Error during loot fetch:', error);
        const resultsDiv = document.getElementById('result');
        resultsDiv.innerHTML = `<h3>Error:</h3><p>${error.message}</p>`;
    }
});
