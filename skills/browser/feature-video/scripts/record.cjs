// Record a real browser workflow as video, one take per role, with a visible cursor,
// click ripples and caption cues.
//
// Run:  BASE_URL=https://site.test [WP_PATH=/path/to/wordpress] node record.cjs <scenario.cjs> <out-dir> [take ...]
//
// The scenario module exports `async (rec) => { ... }`. Inside it:
//
//   const take = await rec.take( '03-checkout', { login: 'admin' } );  // new context + video
//   await take.go( '/checkout/' );                 // navigate, wait for load, tidy the page
//   await take.click( take.page.locator( '#place_order' ) );   // glide the cursor, then click
//   await take.glide( locator ); await take.scrollTo( locator ); await take.pause( 900 );
//   take.mark( 'Pay by card', 'The card is charged on the vendor account.' );  // caption cue at "now"
//   await take.close();                            // saves <out-dir>/03-checkout.webm
//
//   rec.keepNotices = /payout|refund/i;   // hide .notice/.update-nag except ones matching this
//   rec.masks = [ [ /real@email\.com/g, 'buyer@example.org' ] ];   // replaced in text and inputs
//   rec.wp( 'eval "echo 1;"' )            // WP-CLI against WP_PATH, returns stdout
//
// Takes named on the command line are the only ones recorded (the scenario's other
// rec.take() calls return a no-op stub), so one broken take can be re-recorded alone;
// marks.json keeps the cues of the takes not re-recorded.
//
// Login: { login: '<user>' } mints WordPress auth cookies with WP-CLI (needs WP_PATH).
// Pass { cookies: [...] } for anything else. Every dialog (confirm/alert) is accepted.
const { execSync } = require( 'child_process' );
const fs = require( 'fs' );
const path = require( 'path' );

const { chromium } = require( require.resolve( 'playwright', { paths: [ process.cwd(), __dirname ] } ) );

const [ scenarioFile, outArg, ...only ] = process.argv.slice( 2 );

if ( ! scenarioFile || ! outArg ) {
	console.error( 'usage: BASE_URL=... node record.cjs <scenario.cjs> <out-dir> [take ...]' );
	process.exit( 2 );
}

const BASE = ( process.env.BASE_URL || '' ).replace( /\/$/, '' );
const WP_PATH = process.env.WP_PATH || '';
const OUT = path.resolve( outArg );
const [ W, H ] = ( process.env.VIEWPORT || '1440x900' ).split( 'x' ).map( Number );
const SIZE = { width: W, height: H };

if ( ! BASE ) {
	console.error( 'Set BASE_URL to the site under test.' );
	process.exit( 2 );
}

fs.mkdirSync( OUT, { recursive: true } );

const marksFile = path.join( OUT, 'marks.json' );
const previous = fs.existsSync( marksFile ) ? JSON.parse( fs.readFileSync( marksFile, 'utf8' ) ).marks || [] : [];
const marks = only.length ? previous.filter( ( m ) => ! only.includes( m.take ) ) : [];

function shQuote( v ) {
	return `'${ String( v ).replace( /'/g, `'\\''` ) }'`;
}

function wp( args ) {
	if ( ! WP_PATH ) {
		throw new Error( 'WP_PATH is not set; it is needed for WP-CLI.' );
	}

	return execSync( `wp ${ args } --path=${ shQuote( WP_PATH ) }`, { encoding: 'utf8' } ).trim();
}

function wpCookies( login ) {
	const php = `$u = get_user_by( "login", ${ JSON.stringify( login ) } ); if ( ! $u ) { throw new Exception( "no user" ); } $exp = time() + 3 * HOUR_IN_SECONDS; echo wp_json_encode( [ [ "name" => SECURE_AUTH_COOKIE, "value" => wp_generate_auth_cookie( $u->ID, $exp, "secure_auth" ) ], [ "name" => AUTH_COOKIE, "value" => wp_generate_auth_cookie( $u->ID, $exp, "auth" ) ], [ "name" => LOGGED_IN_COOKIE, "value" => wp_generate_auth_cookie( $u->ID, $exp, "logged_in" ) ] ] );`;
	const domain = new URL( BASE ).hostname;

	return JSON.parse( wp( `eval ${ shQuote( php ) }` ) ).map( ( c ) => ( { ...c, domain, path: '/', secure: BASE.startsWith( 'https' ), httpOnly: true } ) );
}

// Playwright's video shows neither the pointer nor clicks; draw both in the page.
const CURSOR = `
(() => {
	const install = () => {
		if ( document.getElementById( '__rec_cursor' ) ) return;
		const c = document.createElement( 'div' );
		c.id = '__rec_cursor';
		c.style.cssText = 'position:fixed;left:0;top:0;width:22px;height:22px;margin:-3px 0 0 -3px;z-index:2147483647;pointer-events:none;';
		c.innerHTML = '<svg width="22" height="22" viewBox="0 0 22 22"><path d="M3 2 L3 18 L7.5 13.8 L10.6 20.5 L13.4 19.2 L10.3 12.6 L16.5 12.6 Z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
		document.documentElement.appendChild( c );
		let pos = [ ${ W / 2 }, ${ H / 2 } ];
		try { pos = JSON.parse( sessionStorage.getItem( '__rec_pos' ) || JSON.stringify( pos ) ); } catch ( e ) {}
		c.style.transform = 'translate(' + pos[0] + 'px,' + pos[1] + 'px)';
		addEventListener( 'mousemove', ( e ) => {
			c.style.transform = 'translate(' + e.clientX + 'px,' + e.clientY + 'px)';
			try { sessionStorage.setItem( '__rec_pos', JSON.stringify( [ e.clientX, e.clientY ] ) ); } catch ( err ) {}
		}, true );
		addEventListener( 'mousedown', ( e ) => {
			const r = document.createElement( 'div' );
			r.style.cssText = 'position:fixed;left:' + ( e.clientX - 18 ) + 'px;top:' + ( e.clientY - 18 ) + 'px;width:36px;height:36px;border-radius:50%;border:3px solid #3b6a4c;background:rgba(59,106,76,.18);z-index:2147483646;pointer-events:none;transition:transform .45s ease-out,opacity .45s ease-out;';
			document.documentElement.appendChild( r );
			requestAnimationFrame( () => { r.style.transform = 'scale(1.9)'; r.style.opacity = '0'; } );
			setTimeout( () => r.remove(), 600 );
		}, true );
	};
	if ( document.readyState === 'loading' ) document.addEventListener( 'DOMContentLoaded', install ); else install();
})();
`;

const rec = { keepNotices: null, masks: [], wp, base: BASE, size: SIZE };

async function tidy( page ) {
	const keep = rec.keepNotices ? rec.keepNotices.source : null;
	const flags = rec.keepNotices ? rec.keepNotices.flags : '';
	const masks = rec.masks.map( ( [ re, to ] ) => [ re.source, re.flags.includes( 'g' ) ? re.flags : re.flags + 'g', to ] );

	await page.evaluate( ( { keep, flags, masks } ) => {
		if ( keep !== null ) {
			const k = new RegExp( keep, flags );
			document.querySelectorAll( '.notice, .update-nag' ).forEach( ( n ) => {
				if ( ! k.test( n.textContent ) ) n.style.display = 'none';
			} );
		}

		if ( masks.length ) {
			const res = masks.map( ( [ s, f, to ] ) => [ new RegExp( s, f ), to ] );
			const walker = document.createTreeWalker( document.body, NodeFilter.SHOW_TEXT );
			for ( let node = walker.nextNode(); node; node = walker.nextNode() ) {
				let t = node.nodeValue;
				res.forEach( ( [ re, to ] ) => { t = t.replace( re, to ); } );
				if ( t !== node.nodeValue ) node.nodeValue = t;
			}
			document.querySelectorAll( 'input, textarea' ).forEach( ( i ) => {
				let v = i.value;
				res.forEach( ( [ re, to ] ) => { v = v.replace( re, to ); } );
				if ( v !== i.value ) i.value = v;
			} );
		}
	}, { keep, flags, masks } ).catch( () => {} );
}

class Take {
	constructor( name ) {
		this.name = name;
	}

	async open( browser, opts = {} ) {
		this.context = await browser.newContext( { ignoreHTTPSErrors: true, viewport: SIZE, recordVideo: { dir: OUT, size: SIZE } } );

		const cookies = opts.cookies || ( opts.login ? wpCookies( opts.login ) : [] );

		if ( cookies.length ) {
			await this.context.addCookies( cookies );
		}

		await this.context.addInitScript( CURSOR );
		this.page = await this.context.newPage();
		this.t0 = Date.now();
		this.page.on( 'dialog', ( d ) => d.accept().catch( () => {} ) );
		this.page.on( 'crash', () => console.log( `[${ this.name }] page crashed` ) );
		this.page.setDefaultTimeout( 45_000 );

		return this;
	}

	now() {
		return ( Date.now() - this.t0 ) / 1000;
	}

	mark( title, text = '' ) {
		marks.push( { take: this.name, t: this.now(), title, text } );
		console.log( `[${ this.name } ${ this.now().toFixed( 1 ) }s] ${ title }` );
	}

	async pause( ms = 900 ) {
		await this.page.waitForTimeout( ms );
	}

	async go( url ) {
		await this.page.goto( url.startsWith( 'http' ) ? url : BASE + url, { waitUntil: 'domcontentloaded' } );
		await this.page.waitForLoadState( 'load' ).catch( () => {} );
		await this.tidy();
		await this.pause( 700 );
	}

	async tidy() {
		await tidy( this.page );
	}

	async glide( locator ) {
		await locator.scrollIntoViewIfNeeded().catch( () => {} );
		const box = await locator.boundingBox();

		if ( box ) {
			await this.page.mouse.move( box.x + box.width / 2, box.y + box.height / 2, { steps: 28 } );
		}

		await this.pause( 250 );
	}

	async click( locator ) {
		await this.glide( locator );
		await locator.click();
	}

	// Type like a person; works inside iframes (frameLocator) too.
	async type( locator, text, delay = 50 ) {
		await locator.click();
		await locator.fill( '' );
		await locator.pressSequentially( text, { delay } );
	}

	async scrollTo( locator ) {
		for ( let i = 0; i < 40; i++ ) {
			const box = await locator.boundingBox();

			if ( ! box ) break;

			const delta = box.y + box.height / 2 - SIZE.height / 2;

			if ( Math.abs( delta ) < 60 ) break;

			await this.page.mouse.wheel( 0, Math.max( -140, Math.min( 140, delta ) ) );
			await this.page.waitForTimeout( 45 );
		}

		await this.pause( 400 );
	}

	async close() {
		await this.pause( 1200 );
		const video = this.page.video();
		await this.context.close();
		const file = path.join( OUT, `${ this.name }.webm` );
		fs.renameSync( await video.path(), file );
		console.log( `saved ${ file }` );
	}
}

// A take the command line did not ask for: any property, call or chain on it
// (take.page.locator( … ).first(), await take.go()) is a no-op that returns the stub.
function skipped( name ) {
	const stub = new Proxy( function () {}, {
		get: ( _, k ) => ( k === 'name' ? name : k === 'then' ? undefined : stub ),
		apply: () => stub,
	} );

	return stub;
}

( async () => {
	const browser = await chromium.launch( {
		headless: process.env.HEADLESS === '1',
		channel: process.env.CHANNEL || 'chrome',
		args: [ `--window-size=${ W },${ H + 140 }` ],
	} );

	rec.take = async ( name, opts ) => ( only.length && ! only.includes( name ) ? skipped( name ) : new Take( name ).open( browser, opts ) );

	try {
		await require( path.resolve( scenarioFile ) )( rec );
	} catch ( error ) {
		console.error( 'RECORDING FAILED:', error.message );
		process.exitCode = 1;
	} finally {
		fs.writeFileSync( marksFile, JSON.stringify( { marks }, null, 2 ) );
		await browser.close();
	}
} )();
