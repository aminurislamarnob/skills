#!/usr/bin/env node
// Capture real WordPress screenshots for plugin docs.
//
//   WP_BASE_URL=http://site.test WP_USERNAME=admin WP_PASSWORD=secret \
//     node capture.mjs shots.json <out-dir>
//
// Run from a directory where `playwright` (or `@playwright/test`) resolves,
// e.g. the plugin root. shots.json is an array of shots:
//
//   {
//     "name": "jobs-list",              // file name, no extension
//     "path": "/wp-admin/edit.php?post_type=jobpress",
//     "selector": "#wpbody-content",    // optional: screenshot one element
//     "pad": 24,                        // optional: CSS px of page around the element
//     "fullPage": true,                 // default true (ignored with selector)
//     "viewport": [1800, 1100],         // CSS px, default 1800x1100
//     "loggedIn": true,                 // default true; false = visitor view
//     "colorScheme": "light",           // or "dark"
//     "click": ["#tab-design"],         // optional: clicks before the shot
//     "fill": { "#search": "designer" },// optional: type into fields first
//     "eval": "wp.data.dispatch(…)",    // optional: JS run in the page (awaited)
//     "waitFor": ".jp-listing",         // optional: selector to wait for
//     "hide": [".notice"],              // optional: hidden before the shot
//     "css": ".x{height:auto!important}",// optional: extra CSS (unclip panels)
//     "format": "jpeg"                  // or "png" (small UI crops)
//   }
//
// wp-admin never goes network-idle (Heartbeat), so pages wait for `load` plus
// a short settle; use `waitFor` for anything rendered later.
//
// Admin notices, the WP update nag, the account ("Howdy, …") item and the
// admin bar on the frontend are
// hidden by default so screenshots show only the plugin.

import { createRequire } from 'node:module';
import { readFileSync, mkdirSync } from 'node:fs';
import { resolve, join } from 'node:path';

const require = createRequire( join( process.cwd(), 'noop.js' ) );
let chromium;
try {
	( { chromium } = require( 'playwright' ) );
} catch {
	( { chromium } = require( '@playwright/test' ) );
}

const [ shotsFile, outDir = 'docs-images' ] = process.argv.slice( 2 );
const base = ( process.env.WP_BASE_URL || '' ).replace( /\/$/, '' );
const user = process.env.WP_USERNAME;
const pass = process.env.WP_PASSWORD;
if ( ! shotsFile || ! base ) {
	console.error( 'Usage: WP_BASE_URL=… WP_USERNAME=… WP_PASSWORD=… node capture.mjs shots.json [out-dir]' );
	process.exit( 1 );
}

const DEFAULT_HIDE = [
	'.notice:not(.jp-keep)',
	'.update-nag',
	'#wpfooter',
	'body:not(.wp-admin) #wpadminbar',
	'#screen-meta-links',
	'#wp-admin-bar-my-account',
];

const shots = JSON.parse( readFileSync( resolve( shotsFile ), 'utf8' ) );
mkdirSync( resolve( outDir ), { recursive: true } );

const browser = await chromium.launch();
const contexts = {};

async function getContext( loggedIn, colorScheme ) {
	const key = `${ loggedIn }-${ colorScheme }`;
	if ( contexts[ key ] ) return contexts[ key ];
	const context = await browser.newContext( { deviceScaleFactor: 2, colorScheme } );
	if ( loggedIn ) {
		const page = await context.newPage();
		await page.goto( `${ base }/wp-login.php` );
		await page.fill( '#user_login', user );
		await page.fill( '#user_pass', pass );
		await page.click( '#wp-submit' );
		await page.waitForURL( ( url ) => ! url.pathname.endsWith( 'wp-login.php' ), { timeout: 15000 } ).catch( () => {
			throw new Error( 'Login failed: check WP_USERNAME / WP_PASSWORD' );
		} );
		await page.close();
	}
	return ( contexts[ key ] = context );
}

let failed = 0;
for ( const shot of shots ) {
	const {
		name, path, selector, fullPage = true, viewport = [ 1800, 1100 ], loggedIn = true,
		colorScheme = 'light', click = [], fill = {}, eval: script, waitFor, pad = 0, css = '', hide = [], format = 'jpeg',
	} = shot;
	const file = join( resolve( outDir ), `${ name }.${ format === 'png' ? 'png' : 'jpg' }` );
	const context = await getContext( loggedIn, colorScheme );
	const page = await context.newPage();
	try {
		await page.setViewportSize( { width: viewport[ 0 ], height: viewport[ 1 ] } );
		const response = await page.goto( base + path, { waitUntil: 'load' } );
		if ( response && response.status() >= 400 ) throw new Error( `HTTP ${ response.status() }` );
		if ( await page.locator( 'body#error-page, body.error404' ).count() ) {
			throw new Error( `error page: ${ ( await page.locator( 'body' ).innerText() ).trim().slice( 0, 80 ) }` );
		}
		for ( const [ sel, value ] of Object.entries( fill ) ) await page.fill( sel, value );
		for ( const sel of click ) {
			await page.click( sel );
			await page.waitForLoadState( 'load' );
			await page.waitForTimeout( 400 );
		}
		if ( script ) {
			await page.evaluate( `(async () => { ${ script } })()` );
			await page.waitForTimeout( 800 );
		}
		if ( waitFor ) await page.waitForSelector( waitFor, { state: 'visible' } );
		await page.addStyleTag( { content: `${ [ ...DEFAULT_HIDE, ...hide ].join( ',' ) }{display:none!important}${ css }` } );
		await page.evaluate( () => document.fonts.ready );
		await page.waitForTimeout( 600 );
		const options = { path: file, type: format === 'png' ? 'png' : 'jpeg', animations: 'disabled' };
		if ( options.type === 'jpeg' ) options.quality = 82;
		if ( selector && pad ) {
			const box = await page.locator( selector ).first().boundingBox();
			const scroll = await page.evaluate( () => ( { x: window.scrollX, y: window.scrollY } ) );
			const x = Math.max( 0, box.x + scroll.x - pad );
			const y = Math.max( 0, box.y + scroll.y - pad );
			await page.screenshot( { ...options, fullPage: true, clip: { x, y, width: box.width + 2 * pad, height: box.height + 2 * pad } } );
		} else if ( selector ) await page.locator( selector ).first().screenshot( options );
		else await page.screenshot( { ...options, fullPage } );
		console.log( `✓ ${ name } → ${ file }` );
	} catch ( error ) {
		failed++;
		console.error( `✗ ${ name } (${ path }): ${ error.message.split( '\n' )[ 0 ] }` );
	} finally {
		await page.close();
	}
}

await browser.close();
process.exit( failed ? 1 : 0 );
