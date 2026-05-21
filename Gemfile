source "https://rubygems.org"

# Jekyll itself.
# We deploy via GitHub Actions (see .github/workflows/jekyll.yml),
# so we are NOT constrained to the old Jekyll 3.9.x that the
# `github-pages` gem pins. Use modern Jekyll directly.
gem "jekyll", "~> 4.3"

# Plugins listed in _config.yml
group :jekyll_plugins do
  gem "jekyll-feed",     "~> 0.17"
  gem "jekyll-seo-tag",  "~> 2.8"
  gem "jekyll-sitemap",  "~> 1.4"
  gem "jekyll-paginate", "~> 1.1"
end

# Standard libraries that were removed from Ruby 3.4+ defaults.
# Jekyll and its dependencies still require them, so declare them here.
gem "csv"
gem "base64"
gem "bigdecimal"
gem "logger"

# Webrick is no longer bundled with newer Ruby.
gem "webrick", "~> 1.8"

# Windows / JRuby compatibility (harmless on macOS / Linux).
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end
gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]
gem "http_parser.rb", "~> 0.6.0", :platforms => [:jruby]
