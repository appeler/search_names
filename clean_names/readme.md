## Clean Names

The script is a modified version of [Clean Names](http://github.com/soodoku/clean-names).

The script takes a csv file with column 'Name' containing 'dirty names'--- names with all different formats: lastname firstname, firstname lastname, middlename lastname firstname etc. (see [sample input file](sample_input.csv)) and produces a csv file that has all the columns of the original csv file and the following columns: 'uniqid', 'FirstName', 'MiddleInitial/Name', 'LastName', 'RomanNumeral', 'Title', 'Suffix' (see [sample output file](sample_output.csv)).

### Installation

1. Clone the repository
2. Navigate to clean-names
3. Install requirements

```
pip install -r requirements.txt
```

### Using Clean Names

Usage: `process_names.py [options]`

#### Command Line Options
```  
 	-h, 	    --help show this help message and exit  
 	-o OUTFILE, --out=OUTFILE  
                  	Output file in CSV (default: sample_output.csv)  
    -c COLUMN,  --column=COLUMN  
                  	Column name in CSV that contains Names (default: Name)    
    -a, 	    --all      	
    			Export all names (do not take duplicate names out)  (default: False)  
```

#### Example
<pre><code> python process_names.py -a sample_input.csv </code></pre>