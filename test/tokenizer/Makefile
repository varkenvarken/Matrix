PYTHON=python
MODULE=matrix
TOKENIZE=$(PYTHON) -m $(MODULE) -t

export PYTHONPATH := ../..

all: positive negative

# we need wildcard expansion here to get a list of individual files
# this will cause the implicit rule to fire for each file
POSITIVES = $(wildcard positive/*.mat)
POSITIVES_TOKS = $(patsubst positive/%.mat,positive/%.tok,$(POSITIVES))

NEGATIVES = $(wildcard negative/*.mat)
NEGATIVES_TOKS = $(patsubst negative/%.mat,negative/%.tok,$(NEGATIVES))

# ignore errors so all tests will be run
# also, make it depend on an empty target so each test will always run regardless
# (this is easier than make it dependent on all kinds of files in the matrix module
# the $< will make sure the input is the first file and not the FORCE also ($^ would do that) 
positive/%.tok : positive/%.mat FORCE
	@- $(TOKENIZE) -o $(basename $@) $< && diff --brief $@ $(basename $@).cmp || echo $< tokenization does not match reference

negative/%.tok : negative/%.mat FORCE
	@- if ! ($(TOKENIZE) -o $(basename $@) $< | grep 'Illegal character' 2>&1 > /dev/null) ; then echo $< tokenization did not report illegal character ; fi

positive: $(POSITIVES_TOKS)

negative: $(NEGATIVES_TOKS)

clean:
	rm -f $(POSITIVES_TOKS) $(NEGATIVES_TOKS)

.PHONY: all positive negative clean 

FORCE:
