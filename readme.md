## Search Names

There are seven kinds of challenges in searching a long list of names in a large text corpus. First, the names on the list may not be in a standard format, for e.g., first name may not always be followed by last name, etc. Second, it isn't clear what to search for. For instance, searching FirstName LastName may not be enough. References to the person may take the form of Prefix LastName, etc. Third, names may be misspelled. Fourth, text may refer to people by their diminutive name (hypocorism), or by their middle name, or diminutive form of their middle name, etc. For instance, citations to Bill Clinton are liable to be much more common than William Clinton. Fifth, names on the list may overlap with names not on the list, especially names of other famous people. For instance, searching for [Maryland politician](https://en.wikipedia.org/wiki/Michael_A._Jackson_(politician)) Michael Jackson may yield lots of false positives. Sixth, names on the list may match other names on the list (duplicates). Seventh, searching is computationally expensive. And searching for a long list over a large corpus is a double whammy.

We address each of the problems. 

Before anything else, use [clean names](clean_names/) to standardize the names on the list. The script appends separate columns for prefix, first_name, last_name, etc. Some human curation will likely still be needed. Do it before going further. After that, use [merge supplementary data](merge_supp_data/) to append other potential prefixes, diminutive norms of the first name, and other names by which the person is known by to the output of [clean names](clean_names/). Next, [preprocess](preprocess/) the search list. In particular, the script does three things:   
1. Converts the data from wide to long: The script creates a separate row for each pattern we want to search for. For instance, if we add 'Bill' as a diminutive name for William, and in the configuration file, say, we want to only search for 'FirstName LastName', the script creates a separate row for 'William Clinton' and 'Bill Clinton', copying all other information across rows. And appends a column called 'search_pattern.'  
2. Deduplicates --- it removes any 'pattern', say 'Prefix LastName' that is duplicated and hence cannot be easily disambiguated in search. (This can be turned off.) and   
3. Removes an ad hoc list of patterns. For instance, patterns matching famous people not on the list, e.g. we can remove 'Michael Jackson' and it won't remove 'Congressman Jackson.'   

Lastly, the [search](search/) script searches patterns in the list in a multi-threaded, parallelized way.  

### The Workflow

1. [Clean Names](clean_names/)
2. [Merge Supplementary Data](merge_supp_data/)
3. [Preprocess](preprocess/)
4. [Search](search/)
