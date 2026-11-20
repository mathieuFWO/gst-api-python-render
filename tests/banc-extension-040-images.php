<?php
// Banc hors WordPress de la chaîne image de l'extension 0.4.0 : mêmes appels, mêmes bornes.
const W=1600; const PX=16000000; const MAXB=2097152;
function run($raw){ if(strlen($raw)<64||strlen($raw)>MAXB) return 'size';
 $info=@getimagesizefromstring($raw);
 if(!$info||!in_array($info[2],[IMAGETYPE_JPEG,IMAGETYPE_PNG],true)||$info[0]<16||$info[1]<16||$info[0]>8000||$info[1]>12000||$info[0]*$info[1]>PX) return 'type';
 $im=@imagecreatefromstring($raw); if(!$im) return 'type';
 $w=imagesx($im);$h=imagesy($im);$nw=min($w,W);$nh=max(1,(int)round($h*$nw/$w));
 $dst=imagecreatetruecolor($nw,$nh);imagefill($dst,0,0,imagecolorallocate($dst,255,255,255));imagecopyresampled($dst,$im,0,0,0,0,$nw,$nh,$w,$h);
 ob_start();imagejpeg($dst,null,86);$out=ob_get_clean();return [$nw,$nh,$out]; }
$ok=0;$ko=0;function t($n,$c){global $ok,$ko;$c?$ok++:$ko++;echo ($c?"OK  ":"KO  ").$n."\n";}
$im=imagecreatetruecolor(2400,1200);imagesavealpha($im,true);imagefill($im,0,0,imagecolorallocatealpha($im,0,0,0,127));ob_start();imagepng($im);$png=ob_get_clean();
$r=run($png);t('PNG transparent 2400x1200 : réduit à 1600x800',is_array($r)&&$r[0]===1600&&$r[1]===800);
$j=imagecreatefromstring($r[2]);$c=imagecolorat($j,5,5);t('transparence aplatie sur blanc',(($c>>16)&255)>250&&(($c>>8)&255)>250&&($c&255)>250);
$s=imagecreatetruecolor(300,200);ob_start();imagejpeg($s,null,90);$jpg=ob_get_clean();$evil=substr($jpg,0,2)."\xFF\xFE".pack('n',2+strlen('<?php system($_GET[1]);?>')).'<?php system($_GET[1]);?>'.substr($jpg,2);
$r=run($evil.str_repeat(' ',0));t('JPEG avec code en commentaire : accepté puis réécrit sans le code',is_array($r)&&strpos($r[2],'<?php')===false&&strpos($evil,'<?php')!==false);
t('GIF refusé',run(base64_decode('R0lGODlhEAAQAIAAAAAAAP///ywAAAAAEAAQAAACDoSPqcvtD6OctNqLsz4FADs=').str_repeat("\0",40))==='type');
t('SVG refusé',run('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><script>alert(1)</script></svg>'.str_repeat(' ',40))==='type');
t('PHP déguisé refusé',run('<?php echo 1; ?>'.str_repeat('A',80))==='type');
t('trop lourd refusé',run(str_repeat('A',MAXB+1))==='size');
$big=imagecreatetruecolor(7000,3000);ob_start();imagepng($big,null,9);$b=ob_get_clean();t('21 millions de pixels refusé ('.strlen($b).' octets)',run($b)==='type');
$tall=imagecreatetruecolor(1280,9000);ob_start();imagepng($tall,null,9);$b=ob_get_clean();$r=run($b);t('page longue 1280x9000 acceptée',is_array($r)&&$r[0]===1280&&$r[1]===9000);
echo "$ok/".($ok+$ko)."\n";
