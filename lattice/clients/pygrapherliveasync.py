


<!DOCTYPE html>
<html>
  <head>
    <meta charset='utf-8'>
    <meta http-equiv="X-UA-Compatible" content="chrome=1">
        <title>lattice/clients/pygrapherliveasync.py at master from micramm/HaeffnerLabLattice - GitHub</title>
    <link rel="search" type="application/opensearchdescription+xml" href="/opensearch.xml" title="GitHub" />
    <link rel="fluid-icon" href="https://github.com/fluidicon.png" title="GitHub" />

    
    

    <meta content="authenticity_token" name="csrf-param" />
<meta content="dv97VGGAos+jn0Q1Vs7RCSgOQ0vSrYGlU6nd2m+Rqzs=" name="csrf-token" />

    <link href="https://a248.e.akamai.net/assets.github.com/stylesheets/bundles/github-b0aa6fd4256a7e5b0eb6be5a1b299c7508b007b4.css" media="screen" rel="stylesheet" type="text/css" />
    

    <script src="https://a248.e.akamai.net/assets.github.com/javascripts/bundles/jquery-e46225f266eba00902b2e5b66fe6fe6a484fb242.js" type="text/javascript"></script>
    <script src="https://a248.e.akamai.net/assets.github.com/javascripts/bundles/github-c88d56a208601de8e021a0f9d998c95f08ab5f18.js" type="text/javascript"></script>
    

      <link rel='permalink' href='/micramm/HaeffnerLabLattice/blob/21e5345baf88ee4d327df21784980932c5726606/lattice/clients/pygrapherliveasync.py'>

    <meta name="description" content="HaeffnerLabLattice hosted on GitHub" />
  <link href="https://github.com/micramm/HaeffnerLabLattice/commits/master.atom" rel="alternate" title="Recent Commits to HaeffnerLabLattice:master" type="application/atom+xml" />

  </head>


  <body class="logged_in page-blob linux vis-public env-production ">
    


    

      <div id="header" class="true clearfix">
        <div class="container clearfix">
          <a class="site-logo" href="https://github.com/">
            <!--[if IE]>
            <img alt="GitHub" class="github-logo" src="https://a248.e.akamai.net/assets.github.com/images/modules/header/logov7.png?1323882717" />
            <img alt="GitHub" class="github-logo-hover" src="https://a248.e.akamai.net/assets.github.com/images/modules/header/logov7-hover.png?1324325358" />
            <![endif]-->
            <img alt="GitHub" class="github-logo-4x" height="30" src="https://a248.e.akamai.net/assets.github.com/images/modules/header/logov7@4x.png?1323882717" />
            <img alt="GitHub" class="github-logo-4x-hover" height="30" src="https://a248.e.akamai.net/assets.github.com/images/modules/header/logov7@4x-hover.png?1324325358" />
          </a>

              
    <div class="topsearch ">
<form action="/search" id="top_search_form" method="get">        <a href="/search" class="advanced-search tooltipped downwards" title="Advanced Search">Advanced Search</a>
        <div class="search placeholder-field js-placeholder-field">
          <label class="placeholder" for="global-search-field">Search…</label>
          <input type="text" class="search my_repos_autocompleter" id="global-search-field" name="q" results="5" /> <input type="submit" value="Search" class="button" />
        </div>
        <input type="hidden" name="type" value="Everything" />
        <input type="hidden" name="repo" value="" />
        <input type="hidden" name="langOverride" value="" />
        <input type="hidden" name="start_value" value="1" />
</form>      <ul class="top-nav">
          <li class="explore"><a href="https://github.com/explore">Explore</a></li>
          <li><a href="https://gist.github.com">Gist</a></li>
          <li><a href="/blog">Blog</a></li>
        <li><a href="http://help.github.com">Help</a></li>
      </ul>
    </div>


            


  <div id="userbox">
    <div id="user">
      <a href="https://github.com/micramm"><img height="20" src="https://secure.gravatar.com/avatar/be7d1dce901817f9f5505eb9b1536782?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-140.png" width="20" /></a>
      <a href="https://github.com/micramm" class="name">micramm</a>
    </div>
    <ul id="user-links">
      <li>
        <a href="/inbox/notifications" id="notifications" class="tooltipped downwards" title="Notifications">
          <span class="icon">Notifications</span>
        </a>
      </li>
      <li><a href="/account" id="settings" class="tooltipped downwards" title="Account Settings"><span class="icon">Account Settings</span></a></li>
      <li><a href="/logout" id="logout" class="tooltipped downwards" title="Log Out"><span class="icon">Log Out</span></a></li>
    </ul>
  </div>



          
        </div>
      </div>

      

            <div class="site">
      <div class="container">
        <div class="pagehead repohead instapaper_ignore readability-menu">


        <div class="title-actions-bar">
          <h1>
            <a href="/micramm">micramm</a> /
            <strong><a href="/micramm/HaeffnerLabLattice" class="js-current-repository">HaeffnerLabLattice</a></strong>
          </h1>
          



              <ul class="pagehead-actions">

          <li class="for-owner"><a href="/micramm/HaeffnerLabLattice/admin" class="minibutton btn-admin "><span><span class="icon"></span>Admin</span></a></li>

          <li class="js-toggler-container watch-button-container on">
            <a href="/micramm/HaeffnerLabLattice/toggle_watch" class="minibutton btn-watch watch-button js-toggler-target" data-method="post" data-remote="true" rel="nofollow"><span><span class="icon"></span>Watch</span></a>
            <a href="/micramm/HaeffnerLabLattice/toggle_watch" class="minibutton btn-watch unwatch-button js-toggler-target" data-method="post" data-remote="true" rel="nofollow"><span><span class="icon"></span>Unwatch</span></a>
          </li>

              <li><a href="/micramm/HaeffnerLabLattice/fork" class="minibutton btn-fork fork-button" data-method="post" rel="nofollow"><span><span class="icon"></span>Fork</span></a></li>

              <li class="nspr">
                <a href="/micramm/HaeffnerLabLattice/pull/new/master" class="minibutton btn-pull-request "><span><span class="icon"></span>Pull Request</span></a>
              </li>


      <li class="repostats">
        <ul class="repo-stats">
          <li class="watchers watching">
            <a href="/micramm/HaeffnerLabLattice/watchers" title="Watchers — You're Watching" class="tooltipped downwards">
              2
            </a>
          </li>
          <li class="forks">
            <a href="/micramm/HaeffnerLabLattice/network" title="Forks - You have a fork" class="tooltipped downwards">
              1
            </a>
          </li>
        </ul>
      </li>
    </ul>

        </div>

          

  <ul class="tabs">
    <li><a href="/micramm/HaeffnerLabLattice" class="selected" highlight="repo_sourcerepo_downloadsrepo_commitsrepo_tagsrepo_branches">Code</a></li>
    <li><a href="/micramm/HaeffnerLabLattice/network" highlight="repo_networkrepo_fork_queue">Network</a>
    <li><a href="/micramm/HaeffnerLabLattice/pulls" highlight="repo_pulls">Pull Requests <span class='counter'>0</span></a></li>


      <li><a href="/micramm/HaeffnerLabLattice/wiki" highlight="repo_wiki">Wiki <span class='counter'>1</span></a></li>

    <li><a href="/micramm/HaeffnerLabLattice/graphs" highlight="repo_graphsrepo_contributors">Stats &amp; Graphs</a></li>

  </ul>

  
<div class="frame frame-center tree-finder" style="display:none"
      data-tree-list-url="/micramm/HaeffnerLabLattice/tree-list/21e5345baf88ee4d327df21784980932c5726606"
      data-blob-url-prefix="/micramm/HaeffnerLabLattice/blob/21e5345baf88ee4d327df21784980932c5726606"
    >

  <div class="breadcrumb">
    <b><a href="/micramm/HaeffnerLabLattice">HaeffnerLabLattice</a></b> /
    <input class="tree-finder-input js-navigation-enable" type="text" name="query" autocomplete="off" spellcheck="false">
  </div>

    <div class="octotip">
      <p>
        <a href="/micramm/HaeffnerLabLattice/dismiss-tree-finder-help" class="dismiss js-dismiss-tree-list-help" title="Hide this notice forever" rel="nofollow">Dismiss</a>
        <strong>Octotip:</strong> You've activated the <em>file finder</em>
        by pressing <span class="kbd">t</span> Start typing to filter the
        file list. Use <span class="kbd badmono">↑</span> and
        <span class="kbd badmono">↓</span> to navigate,
        <span class="kbd">enter</span> to view files.
      </p>
    </div>

  <table class="tree-browser" cellpadding="0" cellspacing="0">
    <tr class="js-header"><th>&nbsp;</th><th>name</th></tr>
    <tr class="js-no-results no-results" style="display: none">
      <th colspan="2">No matching files</th>
    </tr>
    <tbody class="js-results-list js-navigation-container" data-navigation-enable-mouse>
    </tbody>
  </table>
</div>

<div id="jump-to-line" style="display:none">
  <h2>Jump to Line</h2>
  <form>
    <input class="textfield" type="text">
    <div class="full-button">
      <button type="submit" class="classy">
        <span>Go</span>
      </button>
    </div>
  </form>
</div>


<div class="subnav-bar">

  <ul class="actions subnav">
    <li><a href="/micramm/HaeffnerLabLattice/tags" class="blank" highlight="repo_tags">Tags <span class="counter">0</span></a></li>
    <li><a href="/micramm/HaeffnerLabLattice/downloads" class="blank" highlight="repo_downloads">Downloads <span class="counter">0</span></a></li>
    
  </ul>
  
  <ul class="scope">
    <li class="switcher">

      <div class="context-menu-container js-menu-container">
        <a href="#"
           class="minibutton bigger switcher context-menu-button js-menu-target js-commitish-button btn-branch repo-tree"
           data-master-branch="master"
           data-ref="master">
          <span><span class="icon"></span><i>branch:</i> master</span>
        </a>

        <div class="context-pane commitish-context js-menu-content">
          <a href="javascript:;" class="close js-menu-close"></a>
          <div class="context-title">Switch Branches/Tags</div>
          <div class="context-body pane-selector commitish-selector js-filterable-commitishes">
            <div class="filterbar">
              <div class="placeholder-field js-placeholder-field">
                <label class="placeholder" for="context-commitish-filter-field" data-placeholder-mode="sticky">Filter branches/tags</label>
                <input type="text" id="context-commitish-filter-field" class="commitish-filter" />
              </div>

              <ul class="tabs">
                <li><a href="#" data-filter="branches" class="selected">Branches</a></li>
                <li><a href="#" data-filter="tags">Tags</a></li>
              </ul>
            </div>

              <div class="commitish-item branch-commitish selector-item">
                <h4>
                    <a href="/micramm/HaeffnerLabLattice/blob/master/lattice/clients/pygrapherliveasync.py" data-name="master" rel="nofollow">master</a>
                </h4>
              </div>


            <div class="no-results" style="display:none">Nothing to show</div>
          </div>
        </div><!-- /.commitish-context-context -->
      </div>

    </li>
  </ul>

  <ul class="subnav with-scope">
    
    <li><a href="/micramm/HaeffnerLabLattice" class="selected" highlight="repo_source">Files</a></li>
    <li><a href="/micramm/HaeffnerLabLattice/commits/master" highlight="repo_commits">Commits</a></li>
    <li><a href="/micramm/HaeffnerLabLattice/branches" class="" highlight="repo_branches" rel="nofollow">Branches <span class="counter">1</span></a></li>
  </ul>

</div>

  
  
  


          

        </div><!-- /.repohead -->

        




  
  <p class="last-commit">Latest commit to the <strong>master</strong> branch</p>

<div class="commit commit-tease js-details-container">
  <p class="commit-title ">
      <a href="/micramm/HaeffnerLabLattice/commit/21e5345baf88ee4d327df21784980932c5726606" class="message">Autoscroll Button</a>
      
  </p>
  <div class="commit-meta">
    <a href="/micramm/HaeffnerLabLattice/commit/21e5345baf88ee4d327df21784980932c5726606" class="sha-block">commit <span class="sha">21e5345baf</span></a>

    <div class="authorship">
      <img class="gravatar" height="20" src="https://secure.gravatar.com/avatar/f667d31685a807fef6f3def788fab3d4?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-140.png" width="20" />
      <span class="author-name"><a href="/mkokish">mkokish</a></span>
      authored <time class="js-relative-date" datetime="2012-01-28T19:44:24-08:00" title="2012-01-28 19:44:24">January 28, 2012</time>

    </div>
  </div>
</div>


<!-- block_view_fragment_key: views4/v8/blob:v16:a2b08d4f8b31e02819f99904b6bc00f2 -->
  <div id="slider">

    <div class="breadcrumb" data-path="lattice/clients/pygrapherliveasync.py/">
      <b><a href="/micramm/HaeffnerLabLattice/tree/21e5345baf88ee4d327df21784980932c5726606" class="js-rewrite-sha">HaeffnerLabLattice</a></b> / <a href="/micramm/HaeffnerLabLattice/tree/21e5345baf88ee4d327df21784980932c5726606/lattice" class="js-rewrite-sha">lattice</a> / <a href="/micramm/HaeffnerLabLattice/tree/21e5345baf88ee4d327df21784980932c5726606/lattice/clients" class="js-rewrite-sha">clients</a> / pygrapherliveasync.py       <span style="display:none" id="clippy_573" class="clippy-text">lattice/clients/pygrapherliveasync.py</span>
      
      <object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
              width="110"
              height="14"
              class="clippy"
              id="clippy" >
      <param name="movie" value="https://a248.e.akamai.net/assets.github.com/flash/clippy.swf?1315937507?v5"/>
      <param name="allowScriptAccess" value="always" />
      <param name="quality" value="high" />
      <param name="scale" value="noscale" />
      <param NAME="FlashVars" value="id=clippy_573&amp;copied=copied!&amp;copyto=copy to clipboard">
      <param name="bgcolor" value="#FFFFFF">
      <param name="wmode" value="opaque">
      <embed src="https://a248.e.akamai.net/assets.github.com/flash/clippy.swf?1315937507?v5"
             width="110"
             height="14"
             name="clippy"
             quality="high"
             allowScriptAccess="always"
             type="application/x-shockwave-flash"
             pluginspage="http://www.macromedia.com/go/getflashplayer"
             FlashVars="id=clippy_573&amp;copied=copied!&amp;copyto=copy to clipboard"
             bgcolor="#FFFFFF"
             wmode="opaque"
      />
      </object>
      

    </div>

    <div class="frames">
      <div class="frame frame-center" data-path="lattice/clients/pygrapherliveasync.py/" data-permalink-url="/micramm/HaeffnerLabLattice/blob/21e5345baf88ee4d327df21784980932c5726606/lattice/clients/pygrapherliveasync.py" data-title="lattice/clients/pygrapherliveasync.py at master from micramm/HaeffnerLabLattice - GitHub" data-type="blob">
          <ul class="big-actions">
            <li><a class="file-edit-link minibutton js-rewrite-sha" href="/micramm/HaeffnerLabLattice/edit/21e5345baf88ee4d327df21784980932c5726606/lattice/clients/pygrapherliveasync.py" data-method="post" rel="nofollow"><span>Edit this file</span></a></li>
          </ul>

        <div id="files" class="bubble">
          <div class="file">
            <div class="meta">
              <div class="info">
                <span class="icon"><img alt="Txt" height="16" src="https://a248.e.akamai.net/assets.github.com/images/icons/txt.png?1315937507" width="16" /></span>
                <span class="mode" title="File Mode">100644</span>
                  <span>349 lines (295 sloc)</span>
                <span>12.434 kb</span>
              </div>
              <ul class="actions">
                <li><a href="/micramm/HaeffnerLabLattice/raw/master/lattice/clients/pygrapherliveasync.py" id="raw-url">raw</a></li>
                  <li><a href="/micramm/HaeffnerLabLattice/blame/master/lattice/clients/pygrapherliveasync.py">blame</a></li>
                <li><a href="/micramm/HaeffnerLabLattice/commits/master/lattice/clients/pygrapherliveasync.py" rel="nofollow">history</a></li>
              </ul>
            </div>
              <div class="data type-python">
      <table cellpadding="0" cellspacing="0" class="lines">
        <tr>
          <td>
            <pre class="line_numbers"><span id="L1" rel="#L1">1</span>
<span id="L2" rel="#L2">2</span>
<span id="L3" rel="#L3">3</span>
<span id="L4" rel="#L4">4</span>
<span id="L5" rel="#L5">5</span>
<span id="L6" rel="#L6">6</span>
<span id="L7" rel="#L7">7</span>
<span id="L8" rel="#L8">8</span>
<span id="L9" rel="#L9">9</span>
<span id="L10" rel="#L10">10</span>
<span id="L11" rel="#L11">11</span>
<span id="L12" rel="#L12">12</span>
<span id="L13" rel="#L13">13</span>
<span id="L14" rel="#L14">14</span>
<span id="L15" rel="#L15">15</span>
<span id="L16" rel="#L16">16</span>
<span id="L17" rel="#L17">17</span>
<span id="L18" rel="#L18">18</span>
<span id="L19" rel="#L19">19</span>
<span id="L20" rel="#L20">20</span>
<span id="L21" rel="#L21">21</span>
<span id="L22" rel="#L22">22</span>
<span id="L23" rel="#L23">23</span>
<span id="L24" rel="#L24">24</span>
<span id="L25" rel="#L25">25</span>
<span id="L26" rel="#L26">26</span>
<span id="L27" rel="#L27">27</span>
<span id="L28" rel="#L28">28</span>
<span id="L29" rel="#L29">29</span>
<span id="L30" rel="#L30">30</span>
<span id="L31" rel="#L31">31</span>
<span id="L32" rel="#L32">32</span>
<span id="L33" rel="#L33">33</span>
<span id="L34" rel="#L34">34</span>
<span id="L35" rel="#L35">35</span>
<span id="L36" rel="#L36">36</span>
<span id="L37" rel="#L37">37</span>
<span id="L38" rel="#L38">38</span>
<span id="L39" rel="#L39">39</span>
<span id="L40" rel="#L40">40</span>
<span id="L41" rel="#L41">41</span>
<span id="L42" rel="#L42">42</span>
<span id="L43" rel="#L43">43</span>
<span id="L44" rel="#L44">44</span>
<span id="L45" rel="#L45">45</span>
<span id="L46" rel="#L46">46</span>
<span id="L47" rel="#L47">47</span>
<span id="L48" rel="#L48">48</span>
<span id="L49" rel="#L49">49</span>
<span id="L50" rel="#L50">50</span>
<span id="L51" rel="#L51">51</span>
<span id="L52" rel="#L52">52</span>
<span id="L53" rel="#L53">53</span>
<span id="L54" rel="#L54">54</span>
<span id="L55" rel="#L55">55</span>
<span id="L56" rel="#L56">56</span>
<span id="L57" rel="#L57">57</span>
<span id="L58" rel="#L58">58</span>
<span id="L59" rel="#L59">59</span>
<span id="L60" rel="#L60">60</span>
<span id="L61" rel="#L61">61</span>
<span id="L62" rel="#L62">62</span>
<span id="L63" rel="#L63">63</span>
<span id="L64" rel="#L64">64</span>
<span id="L65" rel="#L65">65</span>
<span id="L66" rel="#L66">66</span>
<span id="L67" rel="#L67">67</span>
<span id="L68" rel="#L68">68</span>
<span id="L69" rel="#L69">69</span>
<span id="L70" rel="#L70">70</span>
<span id="L71" rel="#L71">71</span>
<span id="L72" rel="#L72">72</span>
<span id="L73" rel="#L73">73</span>
<span id="L74" rel="#L74">74</span>
<span id="L75" rel="#L75">75</span>
<span id="L76" rel="#L76">76</span>
<span id="L77" rel="#L77">77</span>
<span id="L78" rel="#L78">78</span>
<span id="L79" rel="#L79">79</span>
<span id="L80" rel="#L80">80</span>
<span id="L81" rel="#L81">81</span>
<span id="L82" rel="#L82">82</span>
<span id="L83" rel="#L83">83</span>
<span id="L84" rel="#L84">84</span>
<span id="L85" rel="#L85">85</span>
<span id="L86" rel="#L86">86</span>
<span id="L87" rel="#L87">87</span>
<span id="L88" rel="#L88">88</span>
<span id="L89" rel="#L89">89</span>
<span id="L90" rel="#L90">90</span>
<span id="L91" rel="#L91">91</span>
<span id="L92" rel="#L92">92</span>
<span id="L93" rel="#L93">93</span>
<span id="L94" rel="#L94">94</span>
<span id="L95" rel="#L95">95</span>
<span id="L96" rel="#L96">96</span>
<span id="L97" rel="#L97">97</span>
<span id="L98" rel="#L98">98</span>
<span id="L99" rel="#L99">99</span>
<span id="L100" rel="#L100">100</span>
<span id="L101" rel="#L101">101</span>
<span id="L102" rel="#L102">102</span>
<span id="L103" rel="#L103">103</span>
<span id="L104" rel="#L104">104</span>
<span id="L105" rel="#L105">105</span>
<span id="L106" rel="#L106">106</span>
<span id="L107" rel="#L107">107</span>
<span id="L108" rel="#L108">108</span>
<span id="L109" rel="#L109">109</span>
<span id="L110" rel="#L110">110</span>
<span id="L111" rel="#L111">111</span>
<span id="L112" rel="#L112">112</span>
<span id="L113" rel="#L113">113</span>
<span id="L114" rel="#L114">114</span>
<span id="L115" rel="#L115">115</span>
<span id="L116" rel="#L116">116</span>
<span id="L117" rel="#L117">117</span>
<span id="L118" rel="#L118">118</span>
<span id="L119" rel="#L119">119</span>
<span id="L120" rel="#L120">120</span>
<span id="L121" rel="#L121">121</span>
<span id="L122" rel="#L122">122</span>
<span id="L123" rel="#L123">123</span>
<span id="L124" rel="#L124">124</span>
<span id="L125" rel="#L125">125</span>
<span id="L126" rel="#L126">126</span>
<span id="L127" rel="#L127">127</span>
<span id="L128" rel="#L128">128</span>
<span id="L129" rel="#L129">129</span>
<span id="L130" rel="#L130">130</span>
<span id="L131" rel="#L131">131</span>
<span id="L132" rel="#L132">132</span>
<span id="L133" rel="#L133">133</span>
<span id="L134" rel="#L134">134</span>
<span id="L135" rel="#L135">135</span>
<span id="L136" rel="#L136">136</span>
<span id="L137" rel="#L137">137</span>
<span id="L138" rel="#L138">138</span>
<span id="L139" rel="#L139">139</span>
<span id="L140" rel="#L140">140</span>
<span id="L141" rel="#L141">141</span>
<span id="L142" rel="#L142">142</span>
<span id="L143" rel="#L143">143</span>
<span id="L144" rel="#L144">144</span>
<span id="L145" rel="#L145">145</span>
<span id="L146" rel="#L146">146</span>
<span id="L147" rel="#L147">147</span>
<span id="L148" rel="#L148">148</span>
<span id="L149" rel="#L149">149</span>
<span id="L150" rel="#L150">150</span>
<span id="L151" rel="#L151">151</span>
<span id="L152" rel="#L152">152</span>
<span id="L153" rel="#L153">153</span>
<span id="L154" rel="#L154">154</span>
<span id="L155" rel="#L155">155</span>
<span id="L156" rel="#L156">156</span>
<span id="L157" rel="#L157">157</span>
<span id="L158" rel="#L158">158</span>
<span id="L159" rel="#L159">159</span>
<span id="L160" rel="#L160">160</span>
<span id="L161" rel="#L161">161</span>
<span id="L162" rel="#L162">162</span>
<span id="L163" rel="#L163">163</span>
<span id="L164" rel="#L164">164</span>
<span id="L165" rel="#L165">165</span>
<span id="L166" rel="#L166">166</span>
<span id="L167" rel="#L167">167</span>
<span id="L168" rel="#L168">168</span>
<span id="L169" rel="#L169">169</span>
<span id="L170" rel="#L170">170</span>
<span id="L171" rel="#L171">171</span>
<span id="L172" rel="#L172">172</span>
<span id="L173" rel="#L173">173</span>
<span id="L174" rel="#L174">174</span>
<span id="L175" rel="#L175">175</span>
<span id="L176" rel="#L176">176</span>
<span id="L177" rel="#L177">177</span>
<span id="L178" rel="#L178">178</span>
<span id="L179" rel="#L179">179</span>
<span id="L180" rel="#L180">180</span>
<span id="L181" rel="#L181">181</span>
<span id="L182" rel="#L182">182</span>
<span id="L183" rel="#L183">183</span>
<span id="L184" rel="#L184">184</span>
<span id="L185" rel="#L185">185</span>
<span id="L186" rel="#L186">186</span>
<span id="L187" rel="#L187">187</span>
<span id="L188" rel="#L188">188</span>
<span id="L189" rel="#L189">189</span>
<span id="L190" rel="#L190">190</span>
<span id="L191" rel="#L191">191</span>
<span id="L192" rel="#L192">192</span>
<span id="L193" rel="#L193">193</span>
<span id="L194" rel="#L194">194</span>
<span id="L195" rel="#L195">195</span>
<span id="L196" rel="#L196">196</span>
<span id="L197" rel="#L197">197</span>
<span id="L198" rel="#L198">198</span>
<span id="L199" rel="#L199">199</span>
<span id="L200" rel="#L200">200</span>
<span id="L201" rel="#L201">201</span>
<span id="L202" rel="#L202">202</span>
<span id="L203" rel="#L203">203</span>
<span id="L204" rel="#L204">204</span>
<span id="L205" rel="#L205">205</span>
<span id="L206" rel="#L206">206</span>
<span id="L207" rel="#L207">207</span>
<span id="L208" rel="#L208">208</span>
<span id="L209" rel="#L209">209</span>
<span id="L210" rel="#L210">210</span>
<span id="L211" rel="#L211">211</span>
<span id="L212" rel="#L212">212</span>
<span id="L213" rel="#L213">213</span>
<span id="L214" rel="#L214">214</span>
<span id="L215" rel="#L215">215</span>
<span id="L216" rel="#L216">216</span>
<span id="L217" rel="#L217">217</span>
<span id="L218" rel="#L218">218</span>
<span id="L219" rel="#L219">219</span>
<span id="L220" rel="#L220">220</span>
<span id="L221" rel="#L221">221</span>
<span id="L222" rel="#L222">222</span>
<span id="L223" rel="#L223">223</span>
<span id="L224" rel="#L224">224</span>
<span id="L225" rel="#L225">225</span>
<span id="L226" rel="#L226">226</span>
<span id="L227" rel="#L227">227</span>
<span id="L228" rel="#L228">228</span>
<span id="L229" rel="#L229">229</span>
<span id="L230" rel="#L230">230</span>
<span id="L231" rel="#L231">231</span>
<span id="L232" rel="#L232">232</span>
<span id="L233" rel="#L233">233</span>
<span id="L234" rel="#L234">234</span>
<span id="L235" rel="#L235">235</span>
<span id="L236" rel="#L236">236</span>
<span id="L237" rel="#L237">237</span>
<span id="L238" rel="#L238">238</span>
<span id="L239" rel="#L239">239</span>
<span id="L240" rel="#L240">240</span>
<span id="L241" rel="#L241">241</span>
<span id="L242" rel="#L242">242</span>
<span id="L243" rel="#L243">243</span>
<span id="L244" rel="#L244">244</span>
<span id="L245" rel="#L245">245</span>
<span id="L246" rel="#L246">246</span>
<span id="L247" rel="#L247">247</span>
<span id="L248" rel="#L248">248</span>
<span id="L249" rel="#L249">249</span>
<span id="L250" rel="#L250">250</span>
<span id="L251" rel="#L251">251</span>
<span id="L252" rel="#L252">252</span>
<span id="L253" rel="#L253">253</span>
<span id="L254" rel="#L254">254</span>
<span id="L255" rel="#L255">255</span>
<span id="L256" rel="#L256">256</span>
<span id="L257" rel="#L257">257</span>
<span id="L258" rel="#L258">258</span>
<span id="L259" rel="#L259">259</span>
<span id="L260" rel="#L260">260</span>
<span id="L261" rel="#L261">261</span>
<span id="L262" rel="#L262">262</span>
<span id="L263" rel="#L263">263</span>
<span id="L264" rel="#L264">264</span>
<span id="L265" rel="#L265">265</span>
<span id="L266" rel="#L266">266</span>
<span id="L267" rel="#L267">267</span>
<span id="L268" rel="#L268">268</span>
<span id="L269" rel="#L269">269</span>
<span id="L270" rel="#L270">270</span>
<span id="L271" rel="#L271">271</span>
<span id="L272" rel="#L272">272</span>
<span id="L273" rel="#L273">273</span>
<span id="L274" rel="#L274">274</span>
<span id="L275" rel="#L275">275</span>
<span id="L276" rel="#L276">276</span>
<span id="L277" rel="#L277">277</span>
<span id="L278" rel="#L278">278</span>
<span id="L279" rel="#L279">279</span>
<span id="L280" rel="#L280">280</span>
<span id="L281" rel="#L281">281</span>
<span id="L282" rel="#L282">282</span>
<span id="L283" rel="#L283">283</span>
<span id="L284" rel="#L284">284</span>
<span id="L285" rel="#L285">285</span>
<span id="L286" rel="#L286">286</span>
<span id="L287" rel="#L287">287</span>
<span id="L288" rel="#L288">288</span>
<span id="L289" rel="#L289">289</span>
<span id="L290" rel="#L290">290</span>
<span id="L291" rel="#L291">291</span>
<span id="L292" rel="#L292">292</span>
<span id="L293" rel="#L293">293</span>
<span id="L294" rel="#L294">294</span>
<span id="L295" rel="#L295">295</span>
<span id="L296" rel="#L296">296</span>
<span id="L297" rel="#L297">297</span>
<span id="L298" rel="#L298">298</span>
<span id="L299" rel="#L299">299</span>
<span id="L300" rel="#L300">300</span>
<span id="L301" rel="#L301">301</span>
<span id="L302" rel="#L302">302</span>
<span id="L303" rel="#L303">303</span>
<span id="L304" rel="#L304">304</span>
<span id="L305" rel="#L305">305</span>
<span id="L306" rel="#L306">306</span>
<span id="L307" rel="#L307">307</span>
<span id="L308" rel="#L308">308</span>
<span id="L309" rel="#L309">309</span>
<span id="L310" rel="#L310">310</span>
<span id="L311" rel="#L311">311</span>
<span id="L312" rel="#L312">312</span>
<span id="L313" rel="#L313">313</span>
<span id="L314" rel="#L314">314</span>
<span id="L315" rel="#L315">315</span>
<span id="L316" rel="#L316">316</span>
<span id="L317" rel="#L317">317</span>
<span id="L318" rel="#L318">318</span>
<span id="L319" rel="#L319">319</span>
<span id="L320" rel="#L320">320</span>
<span id="L321" rel="#L321">321</span>
<span id="L322" rel="#L322">322</span>
<span id="L323" rel="#L323">323</span>
<span id="L324" rel="#L324">324</span>
<span id="L325" rel="#L325">325</span>
<span id="L326" rel="#L326">326</span>
<span id="L327" rel="#L327">327</span>
<span id="L328" rel="#L328">328</span>
<span id="L329" rel="#L329">329</span>
<span id="L330" rel="#L330">330</span>
<span id="L331" rel="#L331">331</span>
<span id="L332" rel="#L332">332</span>
<span id="L333" rel="#L333">333</span>
<span id="L334" rel="#L334">334</span>
<span id="L335" rel="#L335">335</span>
<span id="L336" rel="#L336">336</span>
<span id="L337" rel="#L337">337</span>
<span id="L338" rel="#L338">338</span>
<span id="L339" rel="#L339">339</span>
<span id="L340" rel="#L340">340</span>
<span id="L341" rel="#L341">341</span>
<span id="L342" rel="#L342">342</span>
<span id="L343" rel="#L343">343</span>
<span id="L344" rel="#L344">344</span>
<span id="L345" rel="#L345">345</span>
<span id="L346" rel="#L346">346</span>
<span id="L347" rel="#L347">347</span>
<span id="L348" rel="#L348">348</span>
<span id="L349" rel="#L349">349</span>
</pre>
          </td>
          <td width="100%">
                <div class="highlight"><pre><div class='line' id='LC1'><span class="sd">&quot;&quot;&quot;</span></div><div class='line' id='LC2'><span class="sd">Version 2.7</span></div><div class='line' id='LC3'><br/></div><div class='line' id='LC4'><span class="sd">Features:</span></div><div class='line' id='LC5'><br/></div><div class='line' id='LC6'><span class="sd">Autoscroll checkbox</span></div><div class='line' id='LC7'><span class="sd">Fit button, fits all data on the screen</span></div><div class='line' id='LC8'><span class="sd">Opens window upon new dataset</span></div><div class='line' id='LC9'><span class="sd">Opens previous datasets</span></div><div class='line' id='LC10'><span class="sd">Overlays incoming data</span></div><div class='line' id='LC11'><br/></div><div class='line' id='LC12'><span class="sd">&quot;&quot;&quot;</span></div><div class='line' id='LC13'><span class="kn">from</span> <span class="nn">PyQt4</span> <span class="kn">import</span> <span class="n">QtGui</span><span class="p">,</span> <span class="n">QtCore</span></div><div class='line' id='LC14'><span class="kn">from</span> <span class="nn">twisted.internet.defer</span> <span class="kn">import</span> <span class="n">inlineCallbacks</span><span class="p">,</span> <span class="n">returnValue</span><span class="p">,</span> <span class="n">DeferredLock</span><span class="p">,</span> <span class="n">Deferred</span></div><div class='line' id='LC15'><span class="kn">from</span> <span class="nn">twisted.internet.task</span> <span class="kn">import</span> <span class="n">LoopingCall</span></div><div class='line' id='LC16'><span class="c">#from twisted.internet.threads import deferToThread</span></div><div class='line' id='LC17'><span class="c"># Guidatastuff</span></div><div class='line' id='LC18'><span class="kn">from</span> <span class="nn">guidata.qt.QtGui</span> <span class="kn">import</span> <span class="p">(</span><span class="n">QWidget</span><span class="p">,</span> <span class="n">QVBoxLayout</span><span class="p">,</span> <span class="n">QHBoxLayout</span><span class="p">,</span> <span class="n">QPushButton</span><span class="p">,</span> <span class="n">QMainWindow</span><span class="p">)</span></div><div class='line' id='LC19'><span class="kn">from</span> <span class="nn">guidata.qt.QtCore</span> <span class="kn">import</span> <span class="n">SIGNAL</span></div><div class='line' id='LC20'><br/></div><div class='line' id='LC21'><span class="c">#---Import plot widget base class</span></div><div class='line' id='LC22'><span class="kn">from</span> <span class="nn">guiqwt.curve</span> <span class="kn">import</span> <span class="n">CurvePlot</span></div><div class='line' id='LC23'><span class="kn">from</span> <span class="nn">guiqwt.plot</span> <span class="kn">import</span> <span class="n">PlotManager</span></div><div class='line' id='LC24'><span class="kn">from</span> <span class="nn">guiqwt.builder</span> <span class="kn">import</span> <span class="n">make</span></div><div class='line' id='LC25'><span class="kn">from</span> <span class="nn">guidata.configtools</span> <span class="kn">import</span> <span class="n">get_icon</span></div><div class='line' id='LC26'><span class="c">#---</span></div><div class='line' id='LC27'><br/></div><div class='line' id='LC28'><span class="kn">from</span> <span class="nn">guidata.qt.QtGui</span> <span class="kn">import</span> <span class="n">QApplication</span></div><div class='line' id='LC29'><span class="kn">import</span> <span class="nn">scipy.signal</span> <span class="kn">as</span> <span class="nn">sps</span><span class="o">,</span> <span class="nn">scipy.ndimage</span> <span class="kn">as</span> <span class="nn">spi</span></div><div class='line' id='LC30'><span class="kn">import</span> <span class="nn">numpy</span> <span class="kn">as</span> <span class="nn">np</span></div><div class='line' id='LC31'><span class="kn">import</span> <span class="nn">time</span></div><div class='line' id='LC32'><br/></div><div class='line' id='LC33'><span class="n">GraphRefreshTime</span> <span class="o">=</span> <span class="o">.</span><span class="mi">1</span><span class="p">;</span> <span class="c"># s, how often plot updates</span></div><div class='line' id='LC34'><span class="n">scrollfrac</span> <span class="o">=</span> <span class="o">.</span><span class="mi">75</span><span class="p">;</span> <span class="c"># Data reaches this much of the screen before auto-scroll takes place</span></div><div class='line' id='LC35'><span class="n">DIRECTORY</span> <span class="o">=</span> <span class="s">&#39;PMT Counts&#39;</span> <span class="c"># Current working directory</span></div><div class='line' id='LC36'><br/></div><div class='line' id='LC37'><span class="c"># NOTE!! The grapher can only see signals if the signals are created in the same directory that the grapher is in.</span></div><div class='line' id='LC38'><br/></div><div class='line' id='LC39'><span class="k">class</span> <span class="nc">Dataset</span><span class="p">(</span><span class="n">QtCore</span><span class="o">.</span><span class="n">QObject</span><span class="p">):</span></div><div class='line' id='LC40'>&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC41'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="sd">&quot;&quot;&quot;Class to handle incoming data and prepare them for plotting &quot;&quot;&quot;</span></div><div class='line' id='LC42'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">cxn</span><span class="p">,</span> <span class="n">context</span><span class="p">,</span> <span class="n">dataset</span><span class="p">):</span></div><div class='line' id='LC43'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="nb">super</span><span class="p">(</span><span class="n">Dataset</span><span class="p">,</span> <span class="bp">self</span><span class="p">)</span><span class="o">.</span><span class="n">__init__</span><span class="p">()</span></div><div class='line' id='LC44'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">accessingData</span> <span class="o">=</span> <span class="n">DeferredLock</span><span class="p">()</span></div><div class='line' id='LC45'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">cxn</span> <span class="o">=</span> <span class="n">cxn</span></div><div class='line' id='LC46'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">context</span> <span class="o">=</span> <span class="n">context</span> <span class="c"># context of the first dataset in the window</span></div><div class='line' id='LC47'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">dataset</span> <span class="o">=</span> <span class="n">dataset</span></div><div class='line' id='LC48'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">data</span> <span class="o">=</span> <span class="bp">None</span></div><div class='line' id='LC49'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">setupDataListener</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">context</span><span class="p">)</span></div><div class='line' id='LC50'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC51'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># open dataset in order to listen for new data signals in current context        </span></div><div class='line' id='LC52'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="nd">@inlineCallbacks</span></div><div class='line' id='LC53'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">openDataset</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span></div><div class='line' id='LC54'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">yield</span> <span class="bp">self</span><span class="o">.</span><span class="n">cxn</span><span class="o">.</span><span class="n">data_vault</span><span class="o">.</span><span class="n">cd</span><span class="p">(</span><span class="n">DIRECTORY</span><span class="p">,</span> <span class="n">context</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">context</span><span class="p">)</span></div><div class='line' id='LC55'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">yield</span> <span class="bp">self</span><span class="o">.</span><span class="n">cxn</span><span class="o">.</span><span class="n">data_vault</span><span class="o">.</span><span class="n">open</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">dataset</span><span class="p">,</span> <span class="n">context</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">context</span><span class="p">)</span></div><div class='line' id='LC56'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC57'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># sets up the listener for new data</span></div><div class='line' id='LC58'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="nd">@inlineCallbacks</span></div><div class='line' id='LC59'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">setupDataListener</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">context</span><span class="p">):</span></div><div class='line' id='LC60'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">yield</span> <span class="bp">self</span><span class="o">.</span><span class="n">cxn</span><span class="o">.</span><span class="n">data_vault</span><span class="o">.</span><span class="n">signal__data_available</span><span class="p">(</span><span class="mi">11111</span><span class="p">,</span> <span class="n">context</span> <span class="o">=</span> <span class="n">context</span><span class="p">)</span></div><div class='line' id='LC61'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">yield</span> <span class="bp">self</span><span class="o">.</span><span class="n">cxn</span><span class="o">.</span><span class="n">data_vault</span><span class="o">.</span><span class="n">addListener</span><span class="p">(</span><span class="n">listener</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">updateData</span><span class="p">,</span> <span class="n">source</span> <span class="o">=</span> <span class="bp">None</span><span class="p">,</span> <span class="n">ID</span> <span class="o">=</span> <span class="mi">11111</span><span class="p">,</span> <span class="n">context</span> <span class="o">=</span> <span class="n">context</span><span class="p">)</span></div><div class='line' id='LC62'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#self.setupDeferred.callback(True)</span></div><div class='line' id='LC63'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC64'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># new data signal</span></div><div class='line' id='LC65'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">updateData</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class="n">x</span><span class="p">,</span><span class="n">y</span><span class="p">):</span></div><div class='line' id='LC66'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">getData</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">context</span><span class="p">)</span></div><div class='line' id='LC67'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC68'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># returns the current data</span></div><div class='line' id='LC69'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="nd">@inlineCallbacks</span></div><div class='line' id='LC70'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">getData</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class="n">context</span><span class="p">):</span></div><div class='line' id='LC71'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">Data</span> <span class="o">=</span> <span class="k">yield</span> <span class="bp">self</span><span class="o">.</span><span class="n">cxn</span><span class="o">.</span><span class="n">data_vault</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="mi">100</span><span class="p">,</span> <span class="n">context</span> <span class="o">=</span> <span class="n">context</span><span class="p">)</span></div><div class='line' id='LC72'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> <span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">data</span> <span class="o">==</span> <span class="bp">None</span><span class="p">):</span></div><div class='line' id='LC73'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">data</span> <span class="o">=</span> <span class="n">Data</span><span class="o">.</span><span class="n">asarray</span></div><div class='line' id='LC74'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">else</span><span class="p">:</span></div><div class='line' id='LC75'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">yield</span> <span class="bp">self</span><span class="o">.</span><span class="n">accessingData</span><span class="o">.</span><span class="n">acquire</span><span class="p">()</span>         </div><div class='line' id='LC76'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">data</span> <span class="o">=</span> <span class="n">np</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">data</span><span class="p">,</span> <span class="n">Data</span><span class="o">.</span><span class="n">asarray</span><span class="p">,</span> <span class="mi">0</span><span class="p">)</span></div><div class='line' id='LC77'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">accessingData</span><span class="o">.</span><span class="n">release</span><span class="p">()</span></div><div class='line' id='LC78'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC79'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="nd">@inlineCallbacks</span></div><div class='line' id='LC80'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">emptyDataBuffer</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span></div><div class='line' id='LC81'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">yield</span> <span class="bp">self</span><span class="o">.</span><span class="n">accessingData</span><span class="o">.</span><span class="n">acquire</span><span class="p">()</span></div><div class='line' id='LC82'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">del</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">data</span><span class="p">)</span></div><div class='line' id='LC83'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">data</span> <span class="o">=</span> <span class="bp">None</span></div><div class='line' id='LC84'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">accessingData</span><span class="o">.</span><span class="n">release</span><span class="p">()</span></div><div class='line' id='LC85'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC86'><span class="k">class</span> <span class="nc">CanvasWidget</span><span class="p">(</span><span class="n">QWidget</span><span class="p">):</span></div><div class='line' id='LC87'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="sd">&quot;&quot;&quot;</span></div><div class='line' id='LC88'><span class="sd">    Filter testing widget</span></div><div class='line' id='LC89'><span class="sd">    parent: parent widget (QWidget)</span></div><div class='line' id='LC90'><span class="sd">    x, y: NumPy arrays</span></div><div class='line' id='LC91'><span class="sd">    func: function object (the signal filter to be tested)</span></div><div class='line' id='LC92'><span class="sd">    &quot;&quot;&quot;</span></div><div class='line' id='LC93'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">parent</span><span class="p">):</span></div><div class='line' id='LC94'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">QWidget</span><span class="o">.</span><span class="n">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">parent</span><span class="p">)</span></div><div class='line' id='LC95'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">parent</span> <span class="o">=</span> <span class="n">parent</span></div><div class='line' id='LC96'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">dataDict</span> <span class="o">=</span> <span class="p">{}</span></div><div class='line' id='LC97'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">itemDataDict</span> <span class="o">=</span> <span class="p">{}</span></div><div class='line' id='LC98'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">data</span> <span class="o">=</span> <span class="bp">None</span> </div><div class='line' id='LC99'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">setMinimumSize</span><span class="p">(</span><span class="mi">320</span><span class="p">,</span> <span class="mi">200</span><span class="p">)</span></div><div class='line' id='LC100'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#---guiqwt related attributes:</span></div><div class='line' id='LC101'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">plot</span> <span class="o">=</span> <span class="bp">None</span></div><div class='line' id='LC102'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">curve_item</span> <span class="o">=</span> <span class="bp">None</span></div><div class='line' id='LC103'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#---</span></div><div class='line' id='LC104'>&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC105'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># Initialize a place in the dictionary for the dataset</span></div><div class='line' id='LC106'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">initializeDataset</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">dataset</span><span class="p">):</span></div><div class='line' id='LC107'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">dataDict</span><span class="p">[</span><span class="n">dataset</span><span class="p">]</span> <span class="o">=</span> <span class="bp">None</span></div><div class='line' id='LC108'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">initializeCurveItems</span><span class="p">(</span><span class="n">dataset</span><span class="p">)</span></div><div class='line' id='LC109'>&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC110'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">setPlotData</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">dataset</span><span class="p">,</span> <span class="n">data</span><span class="p">):</span></div><div class='line' id='LC111'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> <span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">dataDict</span><span class="p">[</span><span class="n">dataset</span><span class="p">]</span> <span class="o">==</span> <span class="bp">None</span><span class="p">):</span></div><div class='line' id='LC112'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">dataDict</span><span class="p">[</span><span class="n">dataset</span><span class="p">]</span> <span class="o">=</span> <span class="n">data</span></div><div class='line' id='LC113'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">else</span><span class="p">:</span></div><div class='line' id='LC114'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">dataDict</span><span class="p">[</span><span class="n">dataset</span><span class="p">]</span> <span class="o">=</span> <span class="n">np</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">dataDict</span><span class="p">[</span><span class="n">dataset</span><span class="p">],</span> <span class="n">data</span><span class="p">,</span> <span class="mi">0</span><span class="p">)</span></div><div class='line' id='LC115'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC116'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">setup_widget</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">title</span><span class="p">):</span></div><div class='line' id='LC117'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#---Create the plot widget:</span></div><div class='line' id='LC118'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">plot</span> <span class="o">=</span> <span class="n">CurvePlot</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span></div><div class='line' id='LC119'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">plot</span><span class="o">.</span><span class="n">set_antialiasing</span><span class="p">(</span><span class="bp">True</span><span class="p">)</span></div><div class='line' id='LC120'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">xaxis</span><span class="p">,</span> <span class="n">yaxis</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">plot</span><span class="o">.</span><span class="n">get_active_axes</span><span class="p">()</span></div><div class='line' id='LC121'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#return [(dx, xaxis), (dy, yaxis)]</span></div><div class='line' id='LC122'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">plot</span><span class="o">.</span><span class="n">set_axis_limits</span><span class="p">(</span><span class="mi">2</span><span class="p">,</span> <span class="mi">0</span><span class="p">,</span> <span class="mi">500</span><span class="p">)</span></div><div class='line' id='LC123'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#print xaxis</span></div><div class='line' id='LC124'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC125'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#---</span></div><div class='line' id='LC126'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC127'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">vlayout</span> <span class="o">=</span> <span class="n">QVBoxLayout</span><span class="p">()</span></div><div class='line' id='LC128'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">vlayout</span><span class="o">.</span><span class="n">addWidget</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">plot</span><span class="p">)</span></div><div class='line' id='LC129'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">setLayout</span><span class="p">(</span><span class="n">vlayout</span><span class="p">)</span>    </div><div class='line' id='LC130'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC131'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">initializeCurveItems</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">dataset</span><span class="p">):</span></div><div class='line' id='LC132'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">itemDataDict</span><span class="p">[</span><span class="n">dataset</span><span class="p">]</span> <span class="o">=</span> <span class="p">[</span><span class="n">make</span><span class="o">.</span><span class="n">curve</span><span class="p">([],</span> <span class="p">[],</span> <span class="n">color</span><span class="o">=</span><span class="s">&#39;b&#39;</span><span class="p">),</span> <span class="n">make</span><span class="o">.</span><span class="n">curve</span><span class="p">([],</span> <span class="p">[],</span> <span class="n">color</span><span class="o">=</span><span class="s">&#39;g&#39;</span><span class="p">),</span> <span class="n">make</span><span class="o">.</span><span class="n">curve</span><span class="p">([],</span> <span class="p">[],</span> <span class="n">color</span><span class="o">=</span><span class="s">&#39;r&#39;</span><span class="p">)]</span></div><div class='line' id='LC133'><span class="c">#        self.curve_item1 = make.curve([], [], color=&#39;b&#39;)</span></div><div class='line' id='LC134'><span class="c">#        self.curve_item2 = make.curve([], [], color=&#39;g&#39;)</span></div><div class='line' id='LC135'><span class="c">#        self.curve_item3 = make.curve([], [], color=&#39;r&#39;)</span></div><div class='line' id='LC136'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC137'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">items</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">itemDataDict</span><span class="p">[</span><span class="n">dataset</span><span class="p">]</span></div><div class='line' id='LC138'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC139'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">for</span> <span class="n">i</span> <span class="ow">in</span> <span class="n">items</span><span class="p">:</span></div><div class='line' id='LC140'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">plot</span><span class="o">.</span><span class="n">add_item</span><span class="p">(</span><span class="n">i</span><span class="p">)</span>      </div><div class='line' id='LC141'><br/></div><div class='line' id='LC142'><span class="c">#        self.plot.add_item(self.curve_item1)</span></div><div class='line' id='LC143'><span class="c">#        self.plot.add_item(self.curve_item2)</span></div><div class='line' id='LC144'><span class="c">#        self.plot.add_item(self.curve_item3)</span></div><div class='line' id='LC145'><br/></div><div class='line' id='LC146'><br/></div><div class='line' id='LC147'><br/></div><div class='line' id='LC148'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">update_curve</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">dataset</span><span class="p">):</span></div><div class='line' id='LC149'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC150'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">data</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">dataDict</span><span class="p">[</span><span class="n">dataset</span><span class="p">]</span></div><div class='line' id='LC151'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC152'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">x</span> <span class="o">=</span> <span class="n">data</span><span class="o">.</span><span class="n">transpose</span><span class="p">()[</span><span class="mi">0</span><span class="p">]</span></div><div class='line' id='LC153'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">indep</span> <span class="o">=</span> <span class="n">np</span><span class="o">.</span><span class="n">arange</span><span class="p">(</span><span class="n">x</span><span class="o">.</span><span class="n">size</span><span class="p">)</span></div><div class='line' id='LC154'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">y1</span> <span class="o">=</span> <span class="n">data</span><span class="o">.</span><span class="n">transpose</span><span class="p">()[</span><span class="mi">1</span><span class="p">]</span></div><div class='line' id='LC155'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">y2</span> <span class="o">=</span> <span class="n">data</span><span class="o">.</span><span class="n">transpose</span><span class="p">()[</span><span class="mi">2</span><span class="p">]</span></div><div class='line' id='LC156'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">y3</span> <span class="o">=</span> <span class="n">data</span><span class="o">.</span><span class="n">transpose</span><span class="p">()[</span><span class="mi">3</span><span class="p">]</span></div><div class='line' id='LC157'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#---Update curve</span></div><div class='line' id='LC158'><span class="c">#        self.curve_item1.set_data(dep, y1)</span></div><div class='line' id='LC159'><span class="c">#        self.curve_item2.set_data(dep, y2)</span></div><div class='line' id='LC160'><span class="c">#        self.curve_item3.set_data(dep, y3)</span></div><div class='line' id='LC161'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC162'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">itemDataDict</span><span class="p">[</span><span class="n">dataset</span><span class="p">]</span></div><div class='line' id='LC163'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC164'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># could make a for loop here, but need a list for the indep variables</span></div><div class='line' id='LC165'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># this&#39;ll do for now</span></div><div class='line' id='LC166'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">itemDataDict</span><span class="p">[</span><span class="n">dataset</span><span class="p">][</span><span class="mi">0</span><span class="p">]</span><span class="o">.</span><span class="n">set_data</span><span class="p">(</span><span class="n">indep</span><span class="p">,</span> <span class="n">y1</span><span class="p">)</span></div><div class='line' id='LC167'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">itemDataDict</span><span class="p">[</span><span class="n">dataset</span><span class="p">][</span><span class="mi">1</span><span class="p">]</span><span class="o">.</span><span class="n">set_data</span><span class="p">(</span><span class="n">indep</span><span class="p">,</span> <span class="n">y2</span><span class="p">)</span></div><div class='line' id='LC168'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">itemDataDict</span><span class="p">[</span><span class="n">dataset</span><span class="p">][</span><span class="mi">2</span><span class="p">]</span><span class="o">.</span><span class="n">set_data</span><span class="p">(</span><span class="n">indep</span><span class="p">,</span> <span class="n">y3</span><span class="p">)</span></div><div class='line' id='LC169'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC170'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> <span class="bp">self</span><span class="o">.</span><span class="n">parent</span><span class="o">.</span><span class="n">cb1</span><span class="o">.</span><span class="n">isChecked</span><span class="p">():</span></div><div class='line' id='LC171'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">cur</span> <span class="o">=</span> <span class="n">indep</span><span class="o">.</span><span class="n">size</span></div><div class='line' id='LC172'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">xmin</span><span class="p">,</span> <span class="n">xmax</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">plot</span><span class="o">.</span><span class="n">get_axis_limits</span><span class="p">(</span><span class="mi">2</span><span class="p">)</span></div><div class='line' id='LC173'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">xwidth</span> <span class="o">=</span> <span class="n">xmax</span> <span class="o">-</span> <span class="n">xmin</span></div><div class='line' id='LC174'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># if current x position exceeds certain x coordinate, update the screen</span></div><div class='line' id='LC175'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> <span class="p">(</span><span class="n">cur</span> <span class="o">&gt;</span> <span class="n">scrollfrac</span> <span class="o">*</span> <span class="n">xwidth</span> <span class="o">+</span> <span class="n">xmin</span><span class="p">):</span></div><div class='line' id='LC176'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">xmin</span> <span class="o">=</span> <span class="n">cur</span> <span class="o">-</span> <span class="n">xwidth</span><span class="o">/</span><span class="mi">4</span></div><div class='line' id='LC177'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">xmax</span> <span class="o">=</span> <span class="n">xmin</span> <span class="o">+</span> <span class="n">xwidth</span></div><div class='line' id='LC178'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">plot</span><span class="o">.</span><span class="n">set_axis_limits</span><span class="p">(</span><span class="mi">2</span><span class="p">,</span> <span class="n">xmin</span><span class="p">,</span> <span class="n">xmax</span><span class="p">)</span></div><div class='line' id='LC179'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC180'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># Update plot</span></div><div class='line' id='LC181'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">plot</span><span class="o">.</span><span class="n">replot</span><span class="p">()</span></div><div class='line' id='LC182'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#---</span></div><div class='line' id='LC183'>&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC184'>&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC185'><span class="k">class</span> <span class="nc">ApplicationWindow</span><span class="p">(</span><span class="n">QMainWindow</span><span class="p">):</span></div><div class='line' id='LC186'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span></div><div class='line' id='LC187'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">QMainWindow</span><span class="o">.</span><span class="n">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span></div><div class='line' id='LC188'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">setWindowTitle</span><span class="p">(</span><span class="s">&quot;Signal filtering 2 (guiqwt)&quot;</span><span class="p">)</span></div><div class='line' id='LC189'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">setWindowIcon</span><span class="p">(</span><span class="n">get_icon</span><span class="p">(</span><span class="s">&#39;guiqwt.png&#39;</span><span class="p">))</span></div><div class='line' id='LC190'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC191'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">hlayout</span> <span class="o">=</span> <span class="n">QHBoxLayout</span><span class="p">()</span></div><div class='line' id='LC192'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">central_widget</span> <span class="o">=</span> <span class="n">QWidget</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span></div><div class='line' id='LC193'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">central_widget</span><span class="o">.</span><span class="n">setLayout</span><span class="p">(</span><span class="n">hlayout</span><span class="p">)</span></div><div class='line' id='LC194'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">setCentralWidget</span><span class="p">(</span><span class="n">central_widget</span><span class="p">)</span></div><div class='line' id='LC195'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#---guiqwt plot manager</span></div><div class='line' id='LC196'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">manager</span> <span class="o">=</span> <span class="n">PlotManager</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span></div><div class='line' id='LC197'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#---</span></div><div class='line' id='LC198'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC199'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">qmc</span> <span class="o">=</span> <span class="n">CanvasWidget</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span></div><div class='line' id='LC200'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">qmc</span><span class="o">.</span><span class="n">setup_widget</span><span class="p">(</span><span class="s">&quot;Dataset&quot;</span><span class="p">)</span></div><div class='line' id='LC201'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">centralWidget</span><span class="p">()</span><span class="o">.</span><span class="n">layout</span><span class="p">()</span><span class="o">.</span><span class="n">addWidget</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">qmc</span><span class="p">)</span></div><div class='line' id='LC202'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#---Register plot to manager</span></div><div class='line' id='LC203'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">manager</span><span class="o">.</span><span class="n">add_plot</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">qmc</span><span class="o">.</span><span class="n">plot</span><span class="p">)</span></div><div class='line' id='LC204'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#---</span></div><div class='line' id='LC205'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># checkbox to change boundaries</span></div><div class='line' id='LC206'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">cb1</span> <span class="o">=</span> <span class="n">QtGui</span><span class="o">.</span><span class="n">QCheckBox</span><span class="p">(</span><span class="s">&#39;Autoscroll&#39;</span><span class="p">,</span> <span class="bp">self</span><span class="p">)</span></div><div class='line' id='LC207'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">cb1</span><span class="o">.</span><span class="n">move</span><span class="p">(</span><span class="mi">250</span><span class="p">,</span> <span class="mi">28</span><span class="p">)</span></div><div class='line' id='LC208'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># checkbox to change boundaries</span></div><div class='line' id='LC209'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">cb2</span> <span class="o">=</span> <span class="n">QtGui</span><span class="o">.</span><span class="n">QCheckBox</span><span class="p">(</span><span class="s">&#39;Overlay&#39;</span><span class="p">,</span> <span class="bp">self</span><span class="p">)</span></div><div class='line' id='LC210'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">cb2</span><span class="o">.</span><span class="n">move</span><span class="p">(</span><span class="mi">350</span><span class="p">,</span> <span class="mi">28</span><span class="p">)</span>      </div><div class='line' id='LC211'>&nbsp;</div><div class='line' id='LC212'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#---Add toolbar and register manager tools</span></div><div class='line' id='LC213'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">toolbar</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">addToolBar</span><span class="p">(</span><span class="s">&quot;tools&quot;</span><span class="p">)</span></div><div class='line' id='LC214'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">manager</span><span class="o">.</span><span class="n">add_toolbar</span><span class="p">(</span><span class="n">toolbar</span><span class="p">,</span> <span class="nb">id</span><span class="p">(</span><span class="n">toolbar</span><span class="p">))</span></div><div class='line' id='LC215'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">manager</span><span class="o">.</span><span class="n">register_all_curve_tools</span><span class="p">()</span></div><div class='line' id='LC216'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC217'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">closeEvent</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">event</span><span class="p">):</span></div><div class='line' id='LC218'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> <span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">cb2</span><span class="o">.</span><span class="n">isChecked</span><span class="p">()):</span></div><div class='line' id='LC219'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># &quot;uncheck&quot; the overlay checkbox</span></div><div class='line' id='LC220'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">cb2</span><span class="o">.</span><span class="n">toggle</span><span class="p">()</span></div><div class='line' id='LC221'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># Then don&#39;t do anything else since this window closes anyway</span></div><div class='line' id='LC222'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">else</span><span class="p">:</span></div><div class='line' id='LC223'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">pass</span>  </div><div class='line' id='LC224'><br/></div><div class='line' id='LC225'><span class="k">class</span> <span class="nc">FirstWindow</span><span class="p">(</span><span class="n">QtGui</span><span class="o">.</span><span class="n">QMainWindow</span><span class="p">):</span></div><div class='line' id='LC226'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="sd">&quot;&quot;&quot;Creates the opening window&quot;&quot;&quot;</span></div><div class='line' id='LC227'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">parent</span><span class="p">):</span></div><div class='line' id='LC228'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">QtGui</span><span class="o">.</span><span class="n">QMainWindow</span><span class="o">.</span><span class="n">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span></div><div class='line' id='LC229'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">parent</span> <span class="o">=</span> <span class="n">parent</span></div><div class='line' id='LC230'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">setWindowTitle</span><span class="p">(</span><span class="s">&quot;Live Grapher!&quot;</span><span class="p">)</span></div><div class='line' id='LC231'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">openButton</span> <span class="o">=</span> <span class="n">QtGui</span><span class="o">.</span><span class="n">QPushButton</span><span class="p">(</span><span class="s">&quot;Open Dataset&quot;</span><span class="p">,</span> <span class="bp">self</span><span class="p">)</span></div><div class='line' id='LC232'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#MR eventually change this to use a layout, or make this button go in a toolbar. </span></div><div class='line' id='LC233'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">openButton</span><span class="o">.</span><span class="n">setGeometry</span><span class="p">(</span><span class="n">QtCore</span><span class="o">.</span><span class="n">QRect</span><span class="p">(</span><span class="mi">0</span><span class="p">,</span> <span class="mi">0</span><span class="p">,</span> <span class="mi">120</span><span class="p">,</span> <span class="mi">30</span><span class="p">))</span></div><div class='line' id='LC234'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">openButton</span><span class="o">.</span><span class="n">move</span><span class="p">(</span><span class="mi">41</span><span class="p">,</span> <span class="mi">30</span><span class="p">)</span></div><div class='line' id='LC235'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">openButton</span><span class="o">.</span><span class="n">clicked</span><span class="o">.</span><span class="n">connect</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">load_plot</span><span class="p">)</span></div><div class='line' id='LC236'>&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC237'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># asks for a dataset to open if one wasn&#39;t opened already    </span></div><div class='line' id='LC238'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">load_plot</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span></div><div class='line' id='LC239'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">text</span><span class="p">,</span> <span class="n">ok</span> <span class="o">=</span> <span class="n">QtGui</span><span class="o">.</span><span class="n">QInputDialog</span><span class="o">.</span><span class="n">getText</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="s">&#39;Open Dataset&#39;</span><span class="p">,</span> <span class="s">&#39;Enter a dataset:&#39;</span><span class="p">)</span>        </div><div class='line' id='LC240'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> <span class="n">ok</span><span class="p">:</span></div><div class='line' id='LC241'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#MR some type checking that is must be an integer. This won&#39;t be necessary when we switch to the browser.</span></div><div class='line' id='LC242'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">dataset</span> <span class="o">=</span> <span class="nb">int</span><span class="p">(</span><span class="n">text</span><span class="p">)</span></div><div class='line' id='LC243'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">parent</span><span class="o">.</span><span class="n">newDataset</span><span class="p">(</span><span class="n">dataset</span><span class="p">)</span></div><div class='line' id='LC244'>&nbsp;&nbsp;</div><div class='line' id='LC245'><span class="k">class</span> <span class="nc">CONNECTIONS</span><span class="p">(</span><span class="n">QtGui</span><span class="o">.</span><span class="n">QGraphicsObject</span><span class="p">):</span></div><div class='line' id='LC246'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">reactor</span><span class="p">,</span> <span class="n">parent</span><span class="o">=</span><span class="bp">None</span><span class="p">):</span></div><div class='line' id='LC247'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="nb">super</span><span class="p">(</span><span class="n">CONNECTIONS</span><span class="p">,</span> <span class="bp">self</span><span class="p">)</span><span class="o">.</span><span class="n">__init__</span><span class="p">()</span></div><div class='line' id='LC248'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">reactor</span> <span class="o">=</span> <span class="n">reactor</span></div><div class='line' id='LC249'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">dwDict</span> <span class="o">=</span> <span class="p">{}</span> <span class="c"># dictionary relating Dataset and ApplicationWindow</span></div><div class='line' id='LC250'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">connect</span><span class="p">()</span></div><div class='line' id='LC251'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">startTimer</span><span class="p">()</span></div><div class='line' id='LC252'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">introWindow</span> <span class="o">=</span> <span class="n">FirstWindow</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span></div><div class='line' id='LC253'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">introWindow</span><span class="o">.</span><span class="n">show</span><span class="p">()</span></div><div class='line' id='LC254'><br/></div><div class='line' id='LC255'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># connect to the data vault    </span></div><div class='line' id='LC256'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="nd">@inlineCallbacks</span>    </div><div class='line' id='LC257'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">connect</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span></div><div class='line' id='LC258'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="kn">from</span> <span class="nn">labrad.wrappers</span> <span class="kn">import</span> <span class="n">connectAsync</span></div><div class='line' id='LC259'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="kn">from</span> <span class="nn">labrad.types</span> <span class="kn">import</span> <span class="n">Error</span></div><div class='line' id='LC260'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">cxn</span> <span class="o">=</span> <span class="k">yield</span> <span class="n">connectAsync</span><span class="p">()</span></div><div class='line' id='LC261'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">server</span> <span class="o">=</span> <span class="k">yield</span> <span class="bp">self</span><span class="o">.</span><span class="n">cxn</span><span class="o">.</span><span class="n">data_vault</span></div><div class='line' id='LC262'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">yield</span> <span class="bp">self</span><span class="o">.</span><span class="n">setupListeners</span><span class="p">()</span></div><div class='line' id='LC263'>&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC264'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># set up dataset listener    </span></div><div class='line' id='LC265'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="nd">@inlineCallbacks</span></div><div class='line' id='LC266'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">setupListeners</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span>               </div><div class='line' id='LC267'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">yield</span> <span class="bp">self</span><span class="o">.</span><span class="n">server</span><span class="o">.</span><span class="n">signal__new_dataset</span><span class="p">(</span><span class="mi">99999</span><span class="p">)</span><span class="c">#, context = context)</span></div><div class='line' id='LC268'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">yield</span> <span class="bp">self</span><span class="o">.</span><span class="n">server</span><span class="o">.</span><span class="n">addListener</span><span class="p">(</span><span class="n">listener</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">updateDataset</span><span class="p">,</span> <span class="n">source</span> <span class="o">=</span> <span class="bp">None</span><span class="p">,</span> <span class="n">ID</span> <span class="o">=</span> <span class="mi">99999</span><span class="p">)</span><span class="c">#, context = context)</span></div><div class='line' id='LC269'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">yield</span> <span class="bp">self</span><span class="o">.</span><span class="n">cxn</span><span class="o">.</span><span class="n">data_vault</span><span class="o">.</span><span class="n">cd</span><span class="p">(</span><span class="n">DIRECTORY</span><span class="p">)</span></div><div class='line' id='LC270'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">print</span> <span class="s">&#39;Connection established: now listening dataset.&#39;</span></div><div class='line' id='LC271'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC272'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># new dataset signal</span></div><div class='line' id='LC273'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">updateDataset</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class="n">x</span><span class="p">,</span><span class="n">y</span><span class="p">):</span></div><div class='line' id='LC274'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">dataset</span> <span class="o">=</span> <span class="nb">int</span><span class="p">(</span><span class="n">y</span><span class="p">[</span><span class="mi">1</span><span class="p">:</span><span class="mi">5</span><span class="p">])</span></div><div class='line' id='LC275'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">newDataset</span><span class="p">(</span><span class="n">dataset</span><span class="p">)</span></div><div class='line' id='LC276'>&nbsp;</div><div class='line' id='LC277'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># Creates a new dataset and gives it an ID for identifying later (Overlaying)</span></div><div class='line' id='LC278'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="nd">@inlineCallbacks</span></div><div class='line' id='LC279'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">newDataset</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">dataset</span><span class="p">):</span></div><div class='line' id='LC280'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">context</span> <span class="o">=</span> <span class="k">yield</span> <span class="bp">self</span><span class="o">.</span><span class="n">cxn</span><span class="o">.</span><span class="n">context</span><span class="p">()</span></div><div class='line' id='LC281'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">datasetObject</span> <span class="o">=</span> <span class="n">Dataset</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">cxn</span><span class="p">,</span> <span class="n">context</span><span class="p">,</span> <span class="n">dataset</span><span class="p">)</span></div><div class='line' id='LC282'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">yield</span> <span class="n">datasetObject</span><span class="o">.</span><span class="n">openDataset</span><span class="p">()</span></div><div class='line' id='LC283'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#if windows request the overlay, update those. else, create a new window.</span></div><div class='line' id='LC284'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">overlayWindows</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">getOverlayingWindows</span><span class="p">()</span></div><div class='line' id='LC285'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> <span class="n">overlayWindows</span><span class="p">:</span></div><div class='line' id='LC286'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">dwDict</span><span class="p">[</span><span class="n">datasetObject</span><span class="p">]</span> <span class="o">=</span> <span class="n">overlayWindows</span></div><div class='line' id='LC287'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">for</span> <span class="n">window</span> <span class="ow">in</span> <span class="n">overlayWindows</span><span class="p">:</span></div><div class='line' id='LC288'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">window</span><span class="o">.</span><span class="n">qmc</span><span class="o">.</span><span class="n">initializeDataset</span><span class="p">(</span><span class="n">dataset</span><span class="p">)</span></div><div class='line' id='LC289'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">else</span><span class="p">:</span></div><div class='line' id='LC290'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">win</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">newGraph</span><span class="p">()</span></div><div class='line' id='LC291'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#yield win.doneMaking</span></div><div class='line' id='LC292'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">dwDict</span><span class="p">[</span><span class="n">datasetObject</span><span class="p">]</span> <span class="o">=</span> <span class="p">[</span><span class="n">win</span><span class="p">]</span></div><div class='line' id='LC293'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">win</span><span class="o">.</span><span class="n">qmc</span><span class="o">.</span><span class="n">initializeDataset</span><span class="p">(</span><span class="n">dataset</span><span class="p">)</span></div><div class='line' id='LC294'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#del(indep)</span></div><div class='line' id='LC295'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#win.qmc.setPlotParameters()</span></div><div class='line' id='LC296'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#win.qmc.refreshPlots()</span></div><div class='line' id='LC297'><br/></div><div class='line' id='LC298'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># create a new graph, also sets up a Window ID so that if a graph...</span></div><div class='line' id='LC299'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># ... asks for plot Overlay, it can be id</span></div><div class='line' id='LC300'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">newGraph</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span></div><div class='line' id='LC301'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">win</span> <span class="o">=</span> <span class="n">ApplicationWindow</span><span class="p">()</span></div><div class='line' id='LC302'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">win</span><span class="o">.</span><span class="n">show</span><span class="p">()</span></div><div class='line' id='LC303'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c">#time.sleep(2)</span></div><div class='line' id='LC304'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">return</span> <span class="n">win</span></div><div class='line' id='LC305'><br/></div><div class='line' id='LC306'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC307'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">startTimer</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span> </div><div class='line' id='LC308'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">lc</span> <span class="o">=</span> <span class="n">LoopingCall</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">timerEvent</span><span class="p">)</span></div><div class='line' id='LC309'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">lc</span><span class="o">.</span><span class="n">start</span><span class="p">(</span><span class="n">GraphRefreshTime</span><span class="p">)</span></div><div class='line' id='LC310'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC311'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="nd">@inlineCallbacks</span></div><div class='line' id='LC312'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">timerEvent</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span></div><div class='line' id='LC313'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">updatedWindows</span> <span class="o">=</span> <span class="nb">set</span><span class="p">()</span></div><div class='line' id='LC314'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">for</span> <span class="n">datasetObject</span> <span class="ow">in</span> <span class="bp">self</span><span class="o">.</span><span class="n">dwDict</span><span class="o">.</span><span class="n">keys</span><span class="p">():</span></div><div class='line' id='LC315'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># stuff you want timed goes here</span></div><div class='line' id='LC316'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> <span class="p">(</span><span class="n">datasetObject</span><span class="o">.</span><span class="n">data</span> <span class="o">!=</span> <span class="bp">None</span><span class="p">):</span></div><div class='line' id='LC317'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">windowsToDrawOn</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">dwDict</span><span class="p">[</span><span class="n">datasetObject</span><span class="p">]</span></div><div class='line' id='LC318'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">data</span> <span class="o">=</span> <span class="n">datasetObject</span><span class="o">.</span><span class="n">data</span></div><div class='line' id='LC319'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">yield</span> <span class="n">datasetObject</span><span class="o">.</span><span class="n">emptyDataBuffer</span><span class="p">()</span></div><div class='line' id='LC320'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">for</span> <span class="n">i</span> <span class="ow">in</span> <span class="n">windowsToDrawOn</span><span class="p">:</span></div><div class='line' id='LC321'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">i</span><span class="o">.</span><span class="n">qmc</span><span class="o">.</span><span class="n">setPlotData</span><span class="p">(</span><span class="n">datasetObject</span><span class="o">.</span><span class="n">dataset</span><span class="p">,</span> <span class="n">data</span><span class="p">)</span></div><div class='line' id='LC322'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">updatedWindows</span><span class="o">.</span><span class="n">add</span><span class="p">((</span><span class="n">i</span><span class="p">,</span><span class="n">datasetObject</span><span class="o">.</span><span class="n">dataset</span><span class="p">))</span></div><div class='line' id='LC323'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">for</span> <span class="n">window</span><span class="p">,</span><span class="n">dataset</span> <span class="ow">in</span> <span class="n">updatedWindows</span><span class="p">:</span></div><div class='line' id='LC324'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">window</span><span class="o">.</span><span class="n">qmc</span><span class="o">.</span><span class="n">update_curve</span><span class="p">(</span><span class="n">dataset</span><span class="p">)</span></div><div class='line' id='LC325'><br/></div><div class='line' id='LC326'><br/></div><div class='line' id='LC327'>&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC328'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># Cycles through the values in each key for checked Overlay boxes, returns the windows...</span></div><div class='line' id='LC329'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># ...with the overlay button checked</span></div><div class='line' id='LC330'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">def</span> <span class="nf">getOverlayingWindows</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span></div><div class='line' id='LC331'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">overlaidWindows</span> <span class="o">=</span> <span class="p">[]</span></div><div class='line' id='LC332'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">for</span> <span class="n">i</span> <span class="ow">in</span> <span class="bp">self</span><span class="o">.</span><span class="n">dwDict</span><span class="o">.</span><span class="n">keys</span><span class="p">():</span></div><div class='line' id='LC333'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">values</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">dwDict</span><span class="p">[</span><span class="n">i</span><span class="p">]</span></div><div class='line' id='LC334'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">for</span> <span class="n">j</span> <span class="ow">in</span> <span class="n">values</span><span class="p">:</span></div><div class='line' id='LC335'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> <span class="n">j</span><span class="o">.</span><span class="n">cb2</span><span class="o">.</span><span class="n">isChecked</span><span class="p">():</span></div><div class='line' id='LC336'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c"># skip duplicates</span></div><div class='line' id='LC337'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> <span class="n">j</span> <span class="ow">in</span> <span class="bp">self</span><span class="o">.</span><span class="n">overlaidWindows</span><span class="p">:</span></div><div class='line' id='LC338'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">pass</span></div><div class='line' id='LC339'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">else</span><span class="p">:</span></div><div class='line' id='LC340'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="bp">self</span><span class="o">.</span><span class="n">overlaidWindows</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">j</span><span class="p">)</span></div><div class='line' id='LC341'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">return</span> <span class="bp">self</span><span class="o">.</span><span class="n">overlaidWindows</span></div><div class='line' id='LC342'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div class='line' id='LC343'><span class="k">if</span> <span class="n">__name__</span> <span class="o">==</span> <span class="s">&#39;__main__&#39;</span><span class="p">:</span></div><div class='line' id='LC344'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">a</span> <span class="o">=</span> <span class="n">QtGui</span><span class="o">.</span><span class="n">QApplication</span><span class="p">(</span> <span class="p">[]</span> <span class="p">)</span></div><div class='line' id='LC345'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="kn">import</span> <span class="nn">qt4reactor</span></div><div class='line' id='LC346'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">qt4reactor</span><span class="o">.</span><span class="n">install</span><span class="p">()</span></div><div class='line' id='LC347'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="kn">from</span> <span class="nn">twisted.internet</span> <span class="kn">import</span> <span class="n">reactor</span></div><div class='line' id='LC348'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">Connections</span> <span class="o">=</span> <span class="n">CONNECTIONS</span><span class="p">(</span><span class="n">reactor</span><span class="p">)</span></div><div class='line' id='LC349'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="n">reactor</span><span class="o">.</span><span class="n">run</span><span class="p">()</span></div></pre></div>
          </td>
        </tr>
      </table>
  </div>

          </div>
        </div>
      </div>
    </div>

  </div>

<div class="frame frame-loading" style="display:none;" data-tree-list-url="/micramm/HaeffnerLabLattice/tree-list/21e5345baf88ee4d327df21784980932c5726606" data-blob-url-prefix="/micramm/HaeffnerLabLattice/blob/21e5345baf88ee4d327df21784980932c5726606">
  <img src="https://a248.e.akamai.net/assets.github.com/images/modules/ajax/big_spinner_336699.gif?1315937721" height="32" width="32">
</div>

      </div>
      <div class="context-overlay"></div>
    </div>


    <!-- footer -->
    <div id="footer" >
      
  <div class="upper_footer">
     <div class="container clearfix">

       <!--[if IE]><h4 id="blacktocat_ie">GitHub Links</h4><![endif]-->
       <![if !IE]><h4 id="blacktocat">GitHub Links</h4><![endif]>

       <ul class="footer_nav">
         <h4>GitHub</h4>
         <li><a href="https://github.com/about">About</a></li>
         <li><a href="https://github.com/blog">Blog</a></li>
         <li><a href="https://github.com/features">Features</a></li>
         <li><a href="https://github.com/contact">Contact &amp; Support</a></li>
         <li><a href="https://github.com/training">Training</a></li>
         <li><a href="http://enterprise.github.com/">GitHub Enterprise</a></li>
         <li><a href="http://status.github.com/">Site Status</a></li>
       </ul>

       <ul class="footer_nav">
         <h4>Tools</h4>
         <li><a href="http://get.gaug.es/">Gauges: Analyze web traffic</a></li>
         <li><a href="http://speakerdeck.com">Speaker Deck: Presentations</a></li>
         <li><a href="https://gist.github.com">Gist: Code snippets</a></li>
         <li><a href="http://mac.github.com/">GitHub for Mac</a></li>
         <li><a href="http://mobile.github.com/">Issues for iPhone</a></li>
         <li><a href="http://jobs.github.com/">Job Board</a></li>
       </ul>

       <ul class="footer_nav">
         <h4>Extras</h4>
         <li><a href="http://shop.github.com/">GitHub Shop</a></li>
         <li><a href="http://octodex.github.com/">The Octodex</a></li>
       </ul>

       <ul class="footer_nav">
         <h4>Documentation</h4>
         <li><a href="http://help.github.com/">GitHub Help</a></li>
         <li><a href="http://developer.github.com/">Developer API</a></li>
         <li><a href="http://github.github.com/github-flavored-markdown/">GitHub Flavored Markdown</a></li>
         <li><a href="http://pages.github.com/">GitHub Pages</a></li>
       </ul>

     </div><!-- /.site -->
  </div><!-- /.upper_footer -->

<div class="lower_footer">
  <div class="container clearfix">
    <!--[if IE]><div id="legal_ie"><![endif]-->
    <![if !IE]><div id="legal"><![endif]>
      <ul>
          <li><a href="https://github.com/site/terms">Terms of Service</a></li>
          <li><a href="https://github.com/site/privacy">Privacy</a></li>
          <li><a href="https://github.com/security">Security</a></li>
      </ul>

      <p>&copy; 2012 <span id="_rrt" title="0.06755s from fe12.rs.github.com">GitHub</span> Inc. All rights reserved.</p>
    </div><!-- /#legal or /#legal_ie-->

      <div class="sponsor">
        <a href="http://www.rackspace.com" class="logo">
          <img alt="Dedicated Server" height="36" src="https://a248.e.akamai.net/assets.github.com/images/modules/footer/rackspace_logo.png?v2" width="38" />
        </a>
        Powered by the <a href="http://www.rackspace.com ">Dedicated
        Servers</a> and<br/> <a href="http://www.rackspacecloud.com">Cloud
        Computing</a> of Rackspace Hosting<span>&reg;</span>
      </div>
  </div><!-- /.site -->
</div><!-- /.lower_footer -->

    </div><!-- /#footer -->

    

<div id="keyboard_shortcuts_pane" class="instapaper_ignore readability-extra" style="display:none">
  <h2>Keyboard Shortcuts <small><a href="#" class="js-see-all-keyboard-shortcuts">(see all)</a></small></h2>

  <div class="columns threecols">
    <div class="column first">
      <h3>Site wide shortcuts</h3>
      <dl class="keyboard-mappings">
        <dt>s</dt>
        <dd>Focus site search</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>?</dt>
        <dd>Bring up this help dialog</dd>
      </dl>
    </div><!-- /.column.first -->

    <div class="column middle" style='display:none'>
      <h3>Commit list</h3>
      <dl class="keyboard-mappings">
        <dt>j</dt>
        <dd>Move selection down</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>k</dt>
        <dd>Move selection up</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>c <em>or</em> o <em>or</em> enter</dt>
        <dd>Open commit</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>y</dt>
        <dd>Expand URL to its canonical form</dd>
      </dl>
    </div><!-- /.column.first -->

    <div class="column last" style='display:none'>
      <h3>Pull request list</h3>
      <dl class="keyboard-mappings">
        <dt>j</dt>
        <dd>Move selection down</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>k</dt>
        <dd>Move selection up</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>o <em>or</em> enter</dt>
        <dd>Open issue</dd>
      </dl>
    </div><!-- /.columns.last -->

  </div><!-- /.columns.equacols -->

  <div style='display:none'>
    <div class="rule"></div>

    <h3>Issues</h3>

    <div class="columns threecols">
      <div class="column first">
        <dl class="keyboard-mappings">
          <dt>j</dt>
          <dd>Move selection down</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>k</dt>
          <dd>Move selection up</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>x</dt>
          <dd>Toggle selection</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>o <em>or</em> enter</dt>
          <dd>Open issue</dd>
        </dl>
      </div><!-- /.column.first -->
      <div class="column middle">
        <dl class="keyboard-mappings">
          <dt>I</dt>
          <dd>Mark selection as read</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>U</dt>
          <dd>Mark selection as unread</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>e</dt>
          <dd>Close selection</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>y</dt>
          <dd>Remove selection from view</dd>
        </dl>
      </div><!-- /.column.middle -->
      <div class="column last">
        <dl class="keyboard-mappings">
          <dt>c</dt>
          <dd>Create issue</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>l</dt>
          <dd>Create label</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>i</dt>
          <dd>Back to inbox</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>u</dt>
          <dd>Back to issues</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>/</dt>
          <dd>Focus issues search</dd>
        </dl>
      </div>
    </div>
  </div>

  <div style='display:none'>
    <div class="rule"></div>

    <h3>Issues Dashboard</h3>

    <div class="columns threecols">
      <div class="column first">
        <dl class="keyboard-mappings">
          <dt>j</dt>
          <dd>Move selection down</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>k</dt>
          <dd>Move selection up</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>o <em>or</em> enter</dt>
          <dd>Open issue</dd>
        </dl>
      </div><!-- /.column.first -->
    </div>
  </div>

  <div style='display:none'>
    <div class="rule"></div>

    <h3>Network Graph</h3>
    <div class="columns equacols">
      <div class="column first">
        <dl class="keyboard-mappings">
          <dt><span class="badmono">←</span> <em>or</em> h</dt>
          <dd>Scroll left</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt><span class="badmono">→</span> <em>or</em> l</dt>
          <dd>Scroll right</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt><span class="badmono">↑</span> <em>or</em> k</dt>
          <dd>Scroll up</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt><span class="badmono">↓</span> <em>or</em> j</dt>
          <dd>Scroll down</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>t</dt>
          <dd>Toggle visibility of head labels</dd>
        </dl>
      </div><!-- /.column.first -->
      <div class="column last">
        <dl class="keyboard-mappings">
          <dt>shift <span class="badmono">←</span> <em>or</em> shift h</dt>
          <dd>Scroll all the way left</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>shift <span class="badmono">→</span> <em>or</em> shift l</dt>
          <dd>Scroll all the way right</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>shift <span class="badmono">↑</span> <em>or</em> shift k</dt>
          <dd>Scroll all the way up</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>shift <span class="badmono">↓</span> <em>or</em> shift j</dt>
          <dd>Scroll all the way down</dd>
        </dl>
      </div><!-- /.column.last -->
    </div>
  </div>

  <div >
    <div class="rule"></div>
    <div class="columns threecols">
      <div class="column first" >
        <h3>Source Code Browsing</h3>
        <dl class="keyboard-mappings">
          <dt>t</dt>
          <dd>Activates the file finder</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>l</dt>
          <dd>Jump to line</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>w</dt>
          <dd>Switch branch/tag</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>y</dt>
          <dd>Expand URL to its canonical form</dd>
        </dl>
      </div>
    </div>
  </div>
</div>

    <div id="markdown-help" class="instapaper_ignore readability-extra">
  <h2>Markdown Cheat Sheet</h2>

  <div class="cheatsheet-content">

  <div class="mod">
    <div class="col">
      <h3>Format Text</h3>
      <p>Headers</p>
      <pre>
# This is an &lt;h1&gt; tag
## This is an &lt;h2&gt; tag
###### This is an &lt;h6&gt; tag</pre>
     <p>Text styles</p>
     <pre>
*This text will be italic*
_This will also be italic_
**This text will be bold**
__This will also be bold__

*You **can** combine them*
</pre>
    </div>
    <div class="col">
      <h3>Lists</h3>
      <p>Unordered</p>
      <pre>
* Item 1
* Item 2
  * Item 2a
  * Item 2b</pre>
     <p>Ordered</p>
     <pre>
1. Item 1
2. Item 2
3. Item 3
   * Item 3a
   * Item 3b</pre>
    </div>
    <div class="col">
      <h3>Miscellaneous</h3>
      <p>Images</p>
      <pre>
![GitHub Logo](/images/logo.png)
Format: ![Alt Text](url)
</pre>
     <p>Links</p>
     <pre>
http://github.com - automatic!
[GitHub](http://github.com)</pre>
<p>Blockquotes</p>
     <pre>
As Kanye West said:

> We're living the future so
> the present is our past.
</pre>
    </div>
  </div>
  <div class="rule"></div>

  <h3>Code Examples in Markdown</h3>
  <div class="col">
      <p>Syntax highlighting with <a href="http://github.github.com/github-flavored-markdown/" title="GitHub Flavored Markdown" target="_blank">GFM</a></p>
      <pre>
```javascript
function fancyAlert(arg) {
  if(arg) {
    $.facebox({div:'#foo'})
  }
}
```</pre>
    </div>
    <div class="col">
      <p>Or, indent your code 4 spaces</p>
      <pre>
Here is a Python code example
without syntax highlighting:

    def foo:
      if not bar:
        return true</pre>
    </div>
    <div class="col">
      <p>Inline code for comments</p>
      <pre>
I think you should use an
`&lt;addr&gt;` element here instead.</pre>
    </div>
  </div>

  </div>
</div>


    <div class="ajax-error-message">
      <p><span class="icon"></span> Something went wrong with that request. Please try again. <a href="javascript:;" class="ajax-error-dismiss">Dismiss</a></p>
    </div>

    
    
    
  </body>
</html>

