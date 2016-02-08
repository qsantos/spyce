CS      = mcs
LIBDIR  = $(HOME)/.local/share/Steam/SteamApps/common/Kerbal\ Space\ Program/KSP_Data/Managed/
TARGETS = modump.dll

all: $(TARGETS)
	@rm -f $(DEPFILE)

%.dll: %.cs
	@$(CS) -lib:$(LIBDIR)/ -t:library -r:Assembly-CSharp.dll -r:UnityEngine.dll $^ -out:$@

clean:

destroy: clean
	rm -f $(TARGETS)

rebuild: destroy all
