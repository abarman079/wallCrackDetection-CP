import json,sys,time,os,traceback,hashlib,socket,importlib.metadata
from pathlib import Path
spec=json.loads(Path(sys.argv[1]).read_text()); result={'model_id':spec['model_id'],'status':'BLOCKED','evidence_kind':'SYNTHETIC_TENSOR_TECHNICAL_TEST_ONLY'}
try:
    import torch
    torch.manual_seed(42)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(42)
    torch.backends.cudnn.benchmark=False
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(min(4,os.cpu_count() or 1))
    device=torch.device(spec['device'])
    if device.type=='cuda' and not torch.cuda.is_available(): raise RuntimeError('CUDA requested but unavailable')
    # No silent download of pretrained weights. Only a random initialization is tested.
    def no_network(*a,**k): raise RuntimeError('Model worker network disabled: provision and audit weights separately')
    socket.create_connection=no_network; socket.socket.connect=no_network
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    mid=spec['model_id']
    def factory():
        if mid in {'unetpp_effb3','unetpp_convnext_tiny'}:
            import segmentation_models_pytorch as smp
            enc='efficientnet-b3' if mid=='unetpp_effb3' else 'tu-convnext_tiny'
            return smp.UnetPlusPlus(encoder_name=enc,encoder_weights=None,in_channels=3,classes=1,activation=None)
        if mid=='segformer_b0':
            from transformers import SegformerConfig,SegformerForSemanticSegmentation
            config=SegformerConfig(num_channels=3,num_labels=1,depths=[2,2,2,2],hidden_sizes=[32,64,160,256],num_attention_heads=[1,2,5,8],sr_ratios=[8,4,2,1],decoder_hidden_size=256)
            return SegformerForSemanticSegmentation(config)
        repo=spec.get('repo_path')
        if not repo:raise RuntimeError('Attach reviewed official source snapshot and set repository_paths')
        sys.path.insert(0,repo)
        if mid=='dmsrcrack':
            from model import DMSRCrack
            return DMSRCrack(in_channels=3,num_classes=2)
        if mid=='scsegamba':
            from main import get_args_parser
            from models import build_model
            args=get_args_parser().parse_args([])
            args.device=str(device)
            for key in ['resume','pretrained','pretrained_path','checkpoint']:
                if hasattr(args,key):setattr(args,key,'')
            built=build_model(args)
            return built[0] if isinstance(built,tuple) else built
        raise ValueError('Unknown model')
    def tensor_output(out):
        if hasattr(out,'logits'):out=out.logits
        elif isinstance(out,dict):
            keys=[k for k in ['logits','out','pred'] if k in out]
            if len(keys)!=1:raise ValueError('Ambiguous model output mapping; inspect pinned adapter before proceeding')
            out=out[keys[0]]
        elif isinstance(out,(list,tuple)):
            if mid!='dmsrcrack':raise ValueError('Unverified tuple/list contract; inspect official segmentation output')
            out=out[0] # Official DMSRCrack returns (refined segmentation logits, boundary probability).
        if not isinstance(out,torch.Tensor):raise TypeError('Output is not a tensor')
        return out
    start=time.perf_counter();model=factory().to(device);model.train()
    size=spec['size'];x=torch.randn(1,3,size,size,device=device)
    if device.type=='cuda':torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize()
    raw=tensor_output(model(x));raw_shape=list(raw.shape)
    if raw.ndim!=4 or raw.shape[0]!=1 or raw.shape[1]!=1:raise ValueError('Expected Bx1xHxW segmentation output, got '+str(raw_shape))
    if mid=='segformer_b0':
        output=torch.nn.functional.interpolate(raw,size=(size,size),mode='bilinear',align_corners=False)
    else:
        if tuple(raw.shape[-2:])!=(size,size):raise ValueError('Unexpected spatial shape: no silent resize for this architecture')
        output=raw
    if not torch.isfinite(output).all():raise ValueError('Nonfinite output')
    loss=(output.square().mean()+.01*output.mean());loss.backward()
    grads=[p.grad for p in model.parameters() if p.requires_grad and p.grad is not None]
    if not grads or not all(torch.isfinite(g).all() for g in grads) or not any(torch.count_nonzero(g)>0 for g in grads):raise ValueError('Missing/nonfinite/zero gradients')
    # One synthetic step tests mechanics, not the future scientific training loss.
    opt=torch.optim.SGD(model.parameters(),lr=1e-4);opt.step();opt.zero_grad()
    model.eval()
    with torch.no_grad():expected=tensor_output(model(x)).detach().cpu()
    ckpt=Path(spec['checkpoint_path']);torch.save(model.state_dict(),ckpt)
    digest=hashlib.sha256()
    with ckpt.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):digest.update(block)
    result.update(checkpoint_sha256=digest.hexdigest(),checkpoint_bytes=ckpt.stat().st_size)
    del model
    if device.type=='cuda':torch.cuda.empty_cache()
    reloaded=factory().to(device);reloaded.load_state_dict(torch.load(ckpt,map_location=device,weights_only=True));reloaded.eval()
    with torch.no_grad():actual=tensor_output(reloaded(x)).detach().cpu()
    torch.testing.assert_close(actual,expected,rtol=1e-5,atol=1e-6)
    if device.type=='cuda':torch.cuda.synchronize()
    result.update(status='PASS',input_shape=list(x.shape),raw_output_shape=raw_shape,operational_output_shape=list(output.shape),elapsed_seconds=time.perf_counter()-start,parameter_count=sum(p.numel() for p in reloaded.parameters()),peak_cuda_bytes=torch.cuda.max_memory_allocated() if device.type=='cuda' else None,torch_version=torch.__version__,torch_cuda=torch.version.cuda,device=str(device),gradients_checked=len(grads),forward_backward_reload=True,pretrained_weights='NOT_USED_RANDOM_INITIALIZATION',output_semantics='DMSRCrack first output logits; SegFormer/SMP logits; SCSegamba semantics require pinned-source review',throughput_scope='one synthetic step including initialization/save/reload; NOT training throughput')
except Exception as e:
    result.update(error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc()[-12000:])
finally:
    p=spec.get('checkpoint_path')
    if p and Path(p).is_file():Path(p).unlink() # own disposable synthetic checkpoint only
    Path(spec['result_path']).write_text(json.dumps(result,indent=2,allow_nan=False))
