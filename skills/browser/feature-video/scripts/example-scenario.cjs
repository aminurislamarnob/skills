// Example scenario for record.cjs: a WooCommerce admin setting, then a shopper's checkout.
// Copy it next to your work, rename the takes, selectors and cues to the feature you record.
//
// One take per role or per screen sequence; a take is one browser context and one video.
// Call take.mark( title, text ) the moment the step it describes is on screen: marks become
// the captions and the anchors for the voiceover.
module.exports = async ( rec ) => {
	rec.keepNotices = /settings saved|order/i; // admin notices the feature itself shows
	rec.masks = [ [ /pk_(test|live)_[A-Za-z0-9]{8}[A-Za-z0-9]*/g, 'pk_test_••••••••' ] ];

	// 1. Admin: the setting that turns the feature on.
	{
		const take = await rec.take( '01-settings', { login: 'admin' } );
		const page = take.page;

		await take.go( '/wp-admin/admin.php?page=wc-settings&tab=checkout' );
		take.mark( 'Payment settings', 'WooCommerce → Payments lists the gateway.' );
		await take.glide( page.locator( 'table.wc_gateways' ) );
		await take.pause( 1500 );
		await take.close();
	}

	// 2. Shopper: add to cart and pay with a test card.
	{
		const take = await rec.take( '02-checkout', { login: 'customer' } );
		const page = take.page;

		await take.go( '/?add-to-cart=123' );
		await take.go( '/checkout/' );
		take.mark( 'Checkout', 'The shopper fills the billing form once.' );
		await take.scrollTo( page.locator( '#place_order' ) );

		// A Stripe Payment Element lives in an iframe: type into it through frameLocator.
		const card = page.frameLocator( '#payment iframe' ).first();
		take.mark( 'Pay by card', 'Test card 4242 4242 4242 4242.' );
		await take.type( card.locator( 'input[name="number"]' ), '4242424242424242' );
		await take.type( card.locator( 'input[name="expiry"]' ), '1234' );
		await take.type( card.locator( 'input[name="cvc"]' ), '123' );

		await take.click( page.locator( '#place_order' ) );
		await page.waitForURL( /order-received\/(\d+)/, { timeout: 90_000 } );
		take.mark( 'Order paid', 'Back on the thank-you page.' );
		await take.pause( 1800 );
		await take.close();
	}
};
