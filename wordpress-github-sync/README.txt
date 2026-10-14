=== WordPress <--> GitHub Sync ===
Contributors: JamesDiGioia, benbalter  
Tags: github, git, version control, content, collaboration, publishing  
Requires at least: 3.9  
Tested up to: 4.8  
Stable tag: 2.0.0  
License: GPLv2  
License URI: http://www.gnu.org/licenses/gpl-2.0.html  

== Description ==

*A WordPress plugin to sync content with a GitHub repository (or Jekyll site)*

[![Build Status](https://scrutinizer-ci.com/g/mAAdhaTTah/wordpress-github-sync/badges/build.png?b=master)](https://scrutinizer-ci.com/g/mAAdhaTTah/wordpress-github-sync/build-status/master) [![Code Coverage](https://scrutinizer-ci.com/g/mAAdhaTTah/wordpress-github-sync/badges/coverage.png?b=master)](https://scrutinizer-ci.com/g/mAAdhaTTah/wordpress-github-sync/?branch=master) [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/mAAdhaTTah/wordpress-github-sync/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/mAAdhaTTah/wordpress-github-sync/?branch=master)

Ever wish you could collaboratively author content for your WordPress site (or expose change history publicly and accept pull requests from your readers)?

Looking to tinker with Jekyll, but wish you could use WordPress's best-of-breed web editing interface instead of Atom? (gasp!)

Well, now you can! Introducing [WordPress <--> GitHub Sync](https://github.com/mAAdhaTTah/wordpress-github-sync)!

= WordPress <--> GitHub Sync does three things: =

1.  Allows content publishers to version their content in GitHub, exposing "who made what change when" to readers
2.  Allows readers to submit proposed improvements to WordPress-served content via GitHub's Pull Request model
3.  Allows non-technical writers to draft and edit a Jekyll site in WordPress's best-of-breed editing interface

= WordPress <--> GitHub sync might be able to do some other cool things: =

* Allow teams to collaboratively write and edit posts using GitHub (e.g., pull requests, issues, comments)
* Allow you to sync the content of two different WordPress installations via GitHub
* Allow you to stage and preview content before "deploying" to your production server

= How it works =

The sync action is based on two hooks:

1. A per-post sync fired in response to WordPress's `save_post` hook which pushes content to GitHub
2. A sync of all changed files triggered by GitHub's `push` webhook (outbound API call)

== Installation ==

= Using the WordPress Dashboard =

1. Navigate to the 'Add New' in the plugins dashboard
2. Search for 'WordPress GitHub Sync'
3. Click 'Install Now'
4. Activate the plugin on the Plugin dashboard

= Uploading in WordPress Dashboard =

1. Download `wordpress-github-sync.zip` from the WordPress plugins repository.
2. Navigate to the 'Add New' in the plugins dashboard
3. Navigate to the 'Upload' area
4. Select `wordpress-github-sync.zip` from your computer
5. Click 'Install Now'
6. Activate the plugin in the Plugin dashboard

= Using FTP =

1. Download `wordpress-github-sync.zip`
2. Extract the `wordpress-github-sync` directory to your computer
3. Upload the `wordpress-github-sync` directory to the `/wp-content/plugins/` directory
4. Activate the plugin in the Plugin dashboard

= Installing from Source =

Install the plugin and activate it via WordPress's plugin settings page.

  1. `cd wp-content/plugins`
  2. `git clone https://github.com/benbalter/wordpress-github-sync.git`
  3. `cd wordpress-github-sync && composer install`
  4. Activate the plugin in Wordpress' Dashboard > Plugins > Installed Plugins

= Configuring the plugin =

1. [Create a personal oauth token](https://github.com/settings/tokens/new) with the `public_repo` scope. If you'd prefer not to use your account, you can create another GitHub account for this.
2. Configure your GitHub host, repository, secret (defined in the next step),  and OAuth Token on the WordPress <--> GitHub sync settings page within WordPress's administrative interface. Make sure the repository has an initial commit or the export will fail.
3. Create a WebHook within your repository with the provided callback URL and callback secret, using `application/json` as the content type. To set up a webhook on GitHub, head over to the **Settings** page of your repository, and click on **Webhooks & services**. After that, click on **Add webhook**.
4. Click `Export to GitHub` or if you use WP-CLI, run `wp wpghs export all ===` from the command line, where === = the user ID you'd like to commit as.

== Frequently Asked Questions ==

= Markdown Support =

WordPress <--> GitHub Sync exports all posts as `.md` files for better display on GitHub, but all content is exported and imported as its original HTML. To enable writing, importing, and exporting in Markdown, please install and enable [WP-Markdown](https://wordpress.org/plugins/wp-markdown/), and WordPress <--> GitHub Sync will use it to convert your posts to and from Markdown.

You can also activate the Markdown module from [Jetpack](https://wordpress.org/plugins/jetpack/) or the standalone [JP Markdown](https://wordpress.org/plugins/jetpack-markdown/) to save in Markdown and export that version to GitHub.

= Importing from GitHub =

WordPress <--> GitHub Sync is also capable of importing posts directly from GitHub, without creating them in WordPress before hand. In order to have your post imported into GitHub, add this YAML Frontmatter to the top of your .md document:

    ---
    post_title: 'Post Title'
    layout: post_type_probably_post
    published: true_or_false
    ---
    Post goes here.

and fill it out with the data related to the post you're writing. Save the post and commit it directly to the repository. After the post is added to WordPress, an additional commit will be added to the repository, updating the new post with the new information from the database.

Note that WordPress <--> GitHub Sync will *only* import posts from the `master` branch. Changes on other branches will be ignored.

If WordPress <--> GitHub Sync cannot find the author for a given import, it will fallback to the default user as set on the settings page. **Make sure you set this user before you begin importing posts from GitHub.** Without it set, WordPress <--> GitHub Sync will default to no user being set for the author as well as unknown-author revisions.

= Custom Post Type & Status Support =

By default, WordPress <--> GitHub Sync only exports published posts and pages. However, it provides a number of [hooks](https://codex.wordpress.org/Plugin_API) in order to customize its functionality. Check out the [wiki](https://github.com/mAAdhaTTah/wordpress-github-sync/wiki) for complete documentation for these actions and filters.

If you want to export additional post types or draft posts, you'll have to hook into the filters `wpghs_whitelisted_post_types` or `wpghs_whitelisted_post_statuses` respectively.

In `wp-content`, create or open the `mu-plugins` folder and create a plugin file there called `wpghs-custom-filters.php`. In it, paste and modify the below code:

    <?php
    /**
     * Plugin Name:  WordPress-GitHub Sync Custom Filters
     * Plugin URI:   https://github.com/benbalter/wordpress-github-sync
     * Description:  Adds support for custom post types and statuses
     * Version:      1.0.0
     * Author:       James DiGioia
     * Author URI:   https://jamesdigioia.com/
     * License:      GPL2
     */

    add_filter('wpghs_whitelisted_post_types', function ($supported_post_types) {
      return array_merge($supported_post_types, array(
        // add your custom post types here
        'gistpen'
      ));
    });

    add_filter('wpghs_whitelisted_post_statuses', function ($supported_post_statuses) {
      return array_merge($supported_post_statuses, array(
        // additional statuses available: https://codex.wordpress.org/Post_Status
        'draft'
      ));
    });

= Add "Edit|View on GitHub" Link =

If you want to add a link to your posts on GitHub, there are 4 functions WordPress<-->GitHub Sync makes available for you to use in your themes or as part of `the_content` filter:

* `get_the_github_view_url` - returns the URL on GitHub to view the current post
* `get_the_github_view_link` - returns an anchor tag (`<a>`) with its href set the the view url
* `get_the_github_edit_url` - returns the URL on GitHub to edit the current post
* `get_the_github_edit_link` - returns an anchor tag (`<a>`) with its href set the the edit url

All four of these functions must be used in the loop. If you'd like to retrieve these URLs outside of the loop, instantiate a new `WordPress_GitHub_Sync_Post` object and call `github_edit_url` or `github_view_url` respectively on it:

    // $id can be retrieved from a query or elsewhere
    $wpghs_post = new WordPress_GitHub_Sync_Post( $id );
    $url = $wpghs_post->github_view_url();

If you'd like to include an edit link without modifying your theme directly, you can add one of these functions to `the_content` like so:

    add_filter( 'the_content', function( $content ) {
      if( is_page() || is_single() ) {
        $content .= get_the_github_edit_link();
      }
      return $content;
    }, 1000 );

**Shortcodes (v >= XXXX)**


If you wish to add either the bare URL or a link referencing the URL to an individual post, without editing themes, you can add a [shortcode](https://codex.wordpress.org/Shortcode_API) anywhere in your post;

`[wpghs]`

The following optional attributes can also be included in the shortcode
* `target=`
   + `'view'` (default)  the url used will be the *view* URL (`/blob/`).
   + `'edit'`            the url used will be the *edit* URL (`/edit/`).
* `type=`
   + `'link'` (default)  an anchor tag (`<a>`) with href set to the requested URL will be inserted.
   + `'url'`             the the bare requested URL will be inserted.
* `text=`
   + `''` (default)      link text (where `type='link'`, ignored otherwise) will be set to 'View this post on GitHub'.
   + `'text'`          link text (where `type='link'`, ignored otherwise) will be set to 'text' (the supplied text).

For example,

`[wpghs target='view' type='link' text='Here is my post on GitHub']` will produce a HTML anchor tag with href set to the 'view' URL of the post on GitHub, and the link text set to 'Here is my post on GitHub', i.e.

`<a href="https://github.com/USERNAME/REPO/blob/master/_posts/YOURPOST.md">Here is my post on GitHub</a>`

Any or all of the attributes can be left out; defaults will take their place.

= Additional Customizations =

There are a number of other customizations available in WordPress <--> GitHub Sync, including the commit message and YAML front-matter. Want more detail? Check out the [wiki](https://github.com/mAAdhaTTah/wordpress-github-sync/wiki).

= Contributing =

Found a bug? Want to take a stab at [one of the open issues](https://github.com/mAAdhaTTah/wordpress-github-sync/issues)? We'd love your help!

See [the contributing documentation](CONTRIBUTING.md) for details.

= Prior Art =

* [WordPress Post Forking](https://github.com/post-forking/post-forking)
* [WordPress to Jekyll exporter](https://github.com/benbalter/wordpress-to-jekyll-exporter)
* [Writing in public, syncing with GitHub](https://konklone.com/post/writing-in-public-syncing-with-github)

== Changelog ==

This change log follows the Keep a Changelog standards.

= [2.0.0][] =

* **POSSIBLY BREAKING**: Remove handling of custom post meta
    * If you were relying on WPGHS to export custom post meta, use `wpghs_post_meta` filter & `wpghs_pre_import_meta` to handle the meta yourself. See the [documentation][] for more information.
* Switch from `sanitize_title` to `sanitize_file_name`.
    * This should ensure better fidelity to the original filename.
* Don't export `post_date` if post isn't published.
    * `post_date` means the time the post was published. If it's not published, it shouldn't have a `post_date`.
* Overwrite post_date from markdown, allowing remote user to modify publish date.

= [1.7.5][] =

* Fix plugin slug (props @gmays)

= [1.7.2][] =

* Fix messages (props @synchrophoto!)
* Fix Markdown when importing w/ Jetpack (props @lite3!)
* Fix bug in HTTP request on 4.6+
* Update dependencies

= [1.7.0][] =

* Add GitHub link shortcode (props @jonocarroll!)
* Add boot hook (props @kennyfraser!)

= [1.6.1][] =

* Fixed bug where post_meta with the same name as built-in meta keys were getting overwritten

= [1.6.0][] =

* New filters:
    * `wpghs_pre_fetch_all_supported`: Filter the query args before all supported posts are queried.
    * `wpghs_is_post_supported`: Determines whether the post is supported by importing/exporting.
* Bugfix: Set secret to password field. See [#124].
* Bugfix: Fix error when importing branch-deletion webhooks.
* Bugfix: Fix "semaphore is locked" response from webhook. See [#121].
* Bugfix: Correctly display import/export messages in settings page. See [#127].
* Bugfix: Correctly set if post is new only when the matching ID is found in the database.

= [1.5.1][] =

* Added Chinese translation (props @malsony!).
* Updated German translation (props @lsinger!).
* Expire semaphore lock to avoid permanently locked install.

= [1.5.0][] =

* New WP-CLI command:
    * `prime`: Forces WPGHS to fetch the latest commit and save it in the cache.
* New filters:
    * `wpghs_sync_branch`: Branch the WordPress install should sync itself with.
    * `wpghs_commit_msg_tag`: Tag appended to the end of the commit message. Split from message with ` - `. Used to determine if commit has been synced already.
* These two new filters allow you to use WPGHS to keep multiple sites in sync.
    * This is an _advanced feature_. Your configuration may or may not be fully supported. **Use at your own risk.**
* Eliminated some direct database calls in exchange for WP_Query usage.

= [1.4.1][] =

* Fix Database error handling
* Fix bug where WPGHS would interfere with other plugins' AJAX hooks.
* Fix transient key length to <40.

= [1.4.0][] =

* Major rewrite of the plugin internals.
    * *Massively* improved internal architecture.
    * Improved speed.
        * Upgraded caching implementation means updates happen faster.
* Line-endings are now normalize to Unix-style.
    * New filter: `wpghs_line_endings` to set preferred line endings.
* New filter: `wpghs_pre_import_args`
    * Called before post arguments are passed for an imported post.
* New filter: `wpghs_pre_import_meta`
    * Called before post meta is imported from a post.
* BREAKING: Remove reference to global `$wpghs` variable.
    * Use `WordPress_GitHub_Sync::$instance` instead.

= [1.3.4][] =

* Add German translation (props @lsinger).
* Update folder names to default to untranslated.

= [1.3.3][] =

* Fix api bug where API call errors weren't getting kicked up to the calling method.

= [1.3.2][] =

* Fix deleting bug where posts that weren't present in the repo were being added.

= [1.3.1][] =

* Re-add validation of post before exporting.
    * Fixed bug where all post types/statuses were being exported.
* Reverted busted SQL query

= [1.3][] =

* New Feature: Support importing posts from GitHub
* New Feature: Support setting revision and new post users on import.
    * Note: There is a new setting, please selected a default/fallback user and saved the settings.

= [1.2][] =

* New Feature: Support displaying an "Edit|View on GitHub" link.
* Update translation strings and implement pot file generation.
* Redirect user away from settings page page after the import/export process starts.
* Fix autoloader to be PHP 5.2 compatible.

= [1.1.1][] =

* Add WPGHS_Post as param to export content filter.

= [1.1.0][] =

* Add filters for content on import and export.

= [1.0.2][] =

* Hide password-protected posts from being exported to GitHub
* Create post slug if WordPress hasn't created it yet (affects draft exporting)

= [1.0.1][] =

* Remove closure to enable PHP 5.2 compatibility (thanks @pdclark!)

= [1.0.0][] =

* Initial release
* Supports full site sync, Markdown import/export, and custom post type & status support

  [Keep a Changelog standards]: http://keepachangelog.com/
  [Semantic Versioning]: http://semver.org/
  [#124]: https://github.com/mAAdhaTTah/wordpress-github-sync/issues/124
  [#121]: https://github.com/mAAdhaTTah/wordpress-github-sync/issues/121
  [#127]: https://github.com/mAAdhaTTah/wordpress-github-sync/issues/127
  [Unreleased]: https://github.com/mAAdhaTTah/wordpress-github-sync
  [2.0.0]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/2.0.0
  [1.7.5]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.7.5
  [1.7.2]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.7.2
  [1.7.0]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.7.0
  [1.6.1]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.6.1
  [1.6.0]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.6.0
  [1.5.1]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.5.1
  [1.5.0]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.5.0
  [1.4.1]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.4.1
  [1.4.0]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.4.0
  [1.3.4]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.3.4
  [1.3.3]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.3.3
  [1.3.2]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.3.2
  [1.3.1]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.3.1
  [1.3]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.3
  [1.2]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.2
  [1.1.1]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.1.1
  [1.1.0]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.1.0
  [1.0.2]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.0.2
  [1.0.1]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.0.1
  [1.0.0]: https://github.com/mAAdhaTTah/wordpress-github-sync/releases/tag/1.0.0
  [documentation]: https://github.com/mAAdhaTTah/wordpress-github-sync/wiki/Customizing-WordPress-GitHub-Sync-with-Filters
