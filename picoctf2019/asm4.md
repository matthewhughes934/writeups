# Asm4

> What will asm4("picoCTF_75806") return?

## Solution 

Let's look at the file, with some annotations around useful bits:

```
asm4:
	<+0>:	push   ebp
	<+1>:	mov    ebp,esp
	<+3>:	push   ebx
	<+4>:	sub    esp,0x10
	<+7>:	mov    DWORD PTR [ebp-0x10],0x276   # int sum = 0x276
	<+14>:	mov    DWORD PTR [ebp-0xc],0x0      # int i = 0;
	<+21>:	jmp    0x518 <asm4+27>
	<+23>:	add    DWORD PTR [ebp-0xc],0x1      # i++
	<+27>:	mov    edx,DWORD PTR [ebp-0xc]
	<+30>:	mov    eax,DWORD PTR [ebp+0x8]      # arg
	<+33>:	add    eax,edx
	<+35>:	movzx  eax,BYTE PTR [eax]
	<+38>:	test   al,al                        # arg[i] != '\0'
	<+40>:	jne    0x514 <asm4+23>
	<+42>:	mov    DWORD PTR [ebp-0x8],0x1      # int j = 1
	<+49>:	jmp    0x587 <asm4+138>
	<+51>:	mov    edx,DWORD PTR [ebp-0x8]
	<+54>:	mov    eax,DWORD PTR [ebp+0x8]
	<+57>:	add    eax,edx
	<+59>:	movzx  eax,BYTE PTR [eax]
	<+62>:	movsx  edx,al                       # edx = *(arg + j)
	<+65>:	mov    eax,DWORD PTR [ebp-0x8]
	<+68>:	lea    ecx,[eax-0x1]
	<+71>:	mov    eax,DWORD PTR [ebp+0x8]
	<+74>:	add    eax,ecx
	<+76>:	movzx  eax,BYTE PTR [eax]
	<+79>:	movsx  eax,al                       # eax = *(arg + j - 1)
	<+82>:	sub    edx,eax
	<+84>:	mov    eax,edx
	<+86>:	mov    edx,eax                      # edx = *(arg + j) - *(arg + j - 1)
	<+88>:	mov    eax,DWORD PTR [ebp-0x10]
	<+91>:	lea    ebx,[edx+eax*1]              # ebx = sum + edx ^^
	<+94>:	mov    eax,DWORD PTR [ebp-0x8]
	<+97>:	lea    edx,[eax+0x1]
	<+100>:	mov    eax,DWORD PTR [ebp+0x8]
	<+103>:	add    eax,edx
	<+105>:	movzx  eax,BYTE PTR [eax]
	<+108>:	movsx  edx,al                       # edx = *(arg + j + 1)
	<+111>:	mov    ecx,DWORD PTR [ebp-0x8]
	<+114>:	mov    eax,DWORD PTR [ebp+0x8]
	<+117>:	add    eax,ecx
	<+119>:	movzx  eax,BYTE PTR [eax]
	<+122>:	movsx  eax,al                       # eax = *(arg + j) 
	<+125>:	sub    edx,eax
	<+127>:	mov    eax,edx
	<+129>:	add    eax,ebx                      # eax = ebx + *(arg + j + 1) - *(arg + j) 
	<+131>:	mov    DWORD PTR [ebp-0x10],eax     # sum += *(arg + j) - *(arg + j - 1) + *(arg + j + 1) - *(arg + j)
	<+134>:	add    DWORD PTR [ebp-0x8],0x1      # j++
	<+138>:	mov    eax,DWORD PTR [ebp-0xc]
	<+141>:	sub    eax,0x1
	<+144>:	cmp    DWORD PTR [ebp-0x8],eax      # j < i - 1
	<+147>:	jl     0x530 <asm4+51>
	<+149>:	mov    eax,DWORD PTR [ebp-0x10]
	<+152>:	add    esp,0x10
	<+155>:	pop    ebx
	<+156>:	pop    ebp
	<+157>:	ret
```

So it looks to be just running two loops and accessing various bits of the
argument string, the equivalent C is something like:

```c
int asm4 (const char *arg) {
    int i, sum = 0x276;
    for (int i = 0; arg[i] != '\0'; i++)
        ;

    for (int j = 1; j < i - 1; j++)
        sum += arg[j + 1] - arg[j - 1];
    return sum;
}
```

Which can be used to get the solution.
