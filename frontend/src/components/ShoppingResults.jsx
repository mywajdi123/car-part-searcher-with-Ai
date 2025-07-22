import React, { useState } from 'react';
import './ShoppingResults.css';

const ShoppingResults = ({ partData, loading, error }) => {
    const [selectedStore, setSelectedStore] = useState('all');
    const [sortBy, setSortBy] = useState('relevance');

    if (loading) {
        return (
            <div className="shopping-loading">
                <div className="loading-spinner"></div>
                <p>Finding the best deals for your part...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="shopping-error">
                <h3>❌ Unable to Load Shopping Results</h3>
                <p>{error}</p>
                <button onClick={() => window.location.reload()}>Try Again</button>
            </div>
        );
    }

    if (!partData) {
        return (
            <div className="shopping-empty">
                <h3>🛒 Ready to Shop</h3>
                <p>Upload a part image to find where to buy it</p>
            </div>
        );
    }

    // Generate mock shopping results based on part data
    const generateShoppingResults = () => {
        const { part_number, ai_analysis, database_result } = partData;
        const partName = database_result?.data?.part_name || ai_analysis?.part_identification?.part_type || 'Auto Part';

        // Mock results from different retailers
        const retailers = [
            {
                name: 'AutoZone',
                logo: '🔴',
                url: `https://www.autozone.com/search?q=${encodeURIComponent(part_number || partName)}`,
                inStock: true,
                price: '$24.99',
                shipping: 'Free shipping on $35+',
                rating: 4.5,
                reviews: 127
            },
            {
                name: 'Advance Auto Parts',
                logo: '🔵',
                url: `https://shop.advanceautoparts.com/find/search?q=${encodeURIComponent(part_number || partName)}`,
                inStock: true,
                price: '$26.49',
                shipping: 'Free store pickup',
                rating: 4.3,
                reviews: 89
            },
            {
                name: 'O\'Reilly Auto Parts',
                logo: '🟡',
                url: `https://www.oreillyauto.com/search?q=${encodeURIComponent(part_number || partName)}`,
                inStock: true,
                price: '$22.95',
                shipping: 'Same day pickup',
                rating: 4.6,
                reviews: 203
            },
            {
                name: 'Amazon',
                logo: '📦',
                url: `https://www.amazon.com/s?k=${encodeURIComponent(part_number || partName)}+auto+part`,
                inStock: true,
                price: '$19.99',
                shipping: 'Prime 2-day delivery',
                rating: 4.2,
                reviews: 456
            },
            {
                name: 'eBay',
                logo: '🛍️',
                url: `https://www.ebay.com/sch/i.html?_nkw=${encodeURIComponent(part_number || partName)}`,
                inStock: true,
                price: '$18.50',
                shipping: 'Varies by seller',
                rating: 4.1,
                reviews: 234
            },
            {
                name: 'RockAuto',
                logo: '🔧',
                url: `https://www.rockauto.com/en/search/?searchtype=partnumber&q=${encodeURIComponent(part_number || '')}`,
                inStock: true,
                price: '$21.75',
                shipping: 'Calculated at checkout',
                rating: 4.4,
                reviews: 156
            }
        ];

        // Add interchangeable parts if available
        const interchangeable = database_result?.data?.interchangeable || [];

        return { main: retailers, interchangeable };
    };

    const { main: mainResults, interchangeable } = generateShoppingResults();

    const filteredResults = selectedStore === 'all'
        ? mainResults
        : mainResults.filter(result => result.name.toLowerCase().includes(selectedStore.toLowerCase()));

    return (
        <div className="shopping-results">
            {/* Header */}
            <div className="shopping-header">
                <h2>🛒 Where to Buy</h2>
                <div className="part-info">
                    <span className="part-number">
                        {partData.part_number || 'Part Number Not Detected'}
                    </span>
                    <span className="part-name">
                        {partData.database_result?.data?.part_name ||
                            partData.ai_analysis?.part_identification?.part_type ||
                            'Auto Part'}
                    </span>
                </div>
            </div>

            {/* Filters */}
            <div className="shopping-filters">
                <div className="filter-group">
                    <label>Store:</label>
                    <select value={selectedStore} onChange={(e) => setSelectedStore(e.target.value)}>
                        <option value="all">All Stores</option>
                        <option value="autozone">AutoZone</option>
                        <option value="advance">Advance Auto</option>
                        <option value="oreilly">O'Reilly</option>
                        <option value="amazon">Amazon</option>
                        <option value="ebay">eBay</option>
                        <option value="rockauto">RockAuto</option>
                    </select>
                </div>
                <div className="filter-group">
                    <label>Sort by:</label>
                    <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                        <option value="relevance">Relevance</option>
                        <option value="price-low">Price: Low to High</option>
                        <option value="price-high">Price: High to Low</option>
                        <option value="rating">Highest Rated</option>
                    </select>
                </div>
            </div>

            {/* Main Results */}
            <div className="shopping-grid">
                {filteredResults.map((result, index) => (
                    <div key={index} className="store-card">
                        <div className="store-header">
                            <div className="store-info">
                                <span className="store-logo">{result.logo}</span>
                                <h3>{result.name}</h3>
                            </div>
                            <div className={`stock-status ${result.inStock ? 'in-stock' : 'out-stock'}`}>
                                {result.inStock ? '✅ In Stock' : '❌ Out of Stock'}
                            </div>
                        </div>

                        <div className="price-section">
                            <div className="price">{result.price}</div>
                            <div className="shipping">{result.shipping}</div>
                        </div>

                        <div className="rating-section">
                            <div className="rating">
                                {'⭐'.repeat(Math.floor(result.rating))} {result.rating}
                            </div>
                            <div className="reviews">({result.reviews} reviews)</div>
                        </div>

                        <div className="store-actions">
                            <a
                                href={result.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="shop-button primary"
                            >
                                Shop at {result.name}
                            </a>
                            <button className="compare-button">Add to Compare</button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Interchangeable Parts Section */}
            {interchangeable.length > 0 && (
                <div className="interchangeable-section">
                    <h3>🔄 Alternative Parts</h3>
                    <p>These parts may also fit your vehicle:</p>
                    <div className="alternative-parts">
                        {interchangeable.map((part, index) => (
                            <div key={index} className="alternative-card">
                                <div className="alt-part-info">
                                    <h4>{part.part_number}</h4>
                                    <p>{part.brand} - {part.type}</p>
                                    {part.price_range && <span className="price-range">{part.price_range}</span>}
                                </div>
                                <button
                                    className="search-alt-button"
                                    onClick={() => window.open(`https://www.google.com/search?q=${encodeURIComponent(part.part_number)}+auto+part`, '_blank')}
                                >
                                    Search This Part
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Compatible Vehicles */}
            {partData.database_result?.data?.compatibility?.length > 0 && (
                <div className="compatibility-quick-view">
                    <h3>🚗 Fits These Vehicles</h3>
                    <div className="vehicle-list">
                        {partData.database_result.data.compatibility.slice(0, 3).map((vehicle, index) => (
                            <div key={index} className="vehicle-item">
                                <strong>{vehicle.make} {vehicle.model}</strong>
                                <span>{vehicle.years}</span>
                                <span>{vehicle.engines.join(', ')}</span>
                            </div>
                        ))}
                        {partData.database_result.data.compatibility.length > 3 && (
                            <div className="more-vehicles">
                                +{partData.database_result.data.compatibility.length - 3} more vehicles
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Price Comparison Summary */}
            <div className="price-summary">
                <h3>💰 Price Comparison</h3>
                <div className="price-stats">
                    <div className="stat">
                        <label>Lowest Price:</label>
                        <span className="highlight">$18.50</span>
                    </div>
                    <div className="stat">
                        <label>Average Price:</label>
                        <span>$22.44</span>
                    </div>
                    <div className="stat">
                        <label>Potential Savings:</label>
                        <span className="savings">Save up to $7.99</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ShoppingResults;